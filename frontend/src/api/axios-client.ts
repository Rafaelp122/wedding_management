// src/api/axios-client.ts
import Axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../stores/authStore";

declare module "axios" {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}

const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const AXIOS_INSTANCE = Axios.create({ baseURL });

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (error: AxiosError | Error) => void;
  config: InternalAxiosRequestConfig;
}> = [];

const processQueue = (
  error: AxiosError | Error | null,
  token: string | null = null,
) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else if (token) {
      if (prom.config.signal?.aborted) {
        prom.reject(
          new AxiosError(
            "Requisição abortada na fila",
            AxiosError.ERR_CANCELED,
            prom.config,
          ),
        );
      } else {
        prom.resolve(token);
      }
    }
  });
  failedQueue = [];
};

AXIOS_INSTANCE.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = useAuthStore.getState().accessToken;
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

AXIOS_INSTANCE.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          failedQueue.push({ resolve, reject, config: originalRequest });
        })
          .then((token) => {
            if (originalRequest.signal?.aborted) {
              return Promise.reject(
                new AxiosError(
                  "Cancelado",
                  AxiosError.ERR_CANCELED,
                  originalRequest,
                ),
              );
            }
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return AXIOS_INSTANCE(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = useAuthStore.getState().refreshToken;
        if (!refreshToken) {
          throw new Error("Sessão irrecuperável: Refresh token ausente.");
        }

        const { data } = await Axios.post(
          "/api/v1/auth/refresh/",
          { refresh: refreshToken },
          { baseURL, timeout: 5000 },
        );

        const newAccessToken = data.access;
        const newRefreshToken = data.refresh || refreshToken;

        useAuthStore.getState().updateTokens(newAccessToken, newRefreshToken);

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        }

        processQueue(null, newAccessToken);
        return AXIOS_INSTANCE(originalRequest);
      } catch (refreshError) {
        const errorToProcess = Axios.isAxiosError(refreshError)
          ? refreshError
          : refreshError instanceof Error
            ? refreshError
            : new Error(String(refreshError));

        processQueue(errorToProcess, null);
        useAuthStore.getState().logout();
        return Promise.reject(errorToProcess);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  },
);
