import Axios, { AxiosError, type AxiosInstance } from "axios";
import type { InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/authStore";
import { normalizeError } from "@/api/utils/normalize-error";
import { createQueue } from "@/api/utils/queue-manager";

async function retryQueuedRequest(
  token: string,
  request: InternalAxiosRequestConfig,
  instance: AxiosInstance,
) {
  if (request.signal?.aborted) {
    throw new AxiosError("Cancelado", AxiosError.ERR_CANCELED, request);
  }
  if (request.headers) {
    request.headers.Authorization = `Bearer ${token}`;
  }
  return instance(request);
}

async function performRefresh(
  originalRequest: InternalAxiosRequestConfig,
  instance: AxiosInstance,
  baseURL: string,
  onTokensUpdated: (access: string, refresh: string) => void,
  onQueueProcessed: (token: string) => void,
) {
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

  onTokensUpdated(newAccessToken, newRefreshToken);

  if (originalRequest.headers) {
    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
  }

  onQueueProcessed(newAccessToken);
  return instance(originalRequest);
}

export function addAuthRefreshInterceptor(instance: AxiosInstance) {
  let isRefreshing = false;
  const queue = createQueue();

  const baseURL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const handleTokensUpdated = (access: string, refresh: string) => {
    useAuthStore.getState().updateTokens(access, refresh);
  };
  const handleQueueProcessed = (token: string) => queue.process(null, token);

  instance.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config as InternalAxiosRequestConfig;

      if (error.response?.status !== 401 || originalRequest._retry) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string>((resolve, reject) => {
          queue.enqueue({ resolve, reject, config: originalRequest });
        })
          .then((token) =>
            retryQueuedRequest(token, originalRequest, instance),
          )
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        return await performRefresh(
          originalRequest,
          instance,
          baseURL,
          handleTokensUpdated,
          handleQueueProcessed,
        );
      } catch (refreshError) {
        const errorToProcess = normalizeError(refreshError);
        queue.process(errorToProcess, null);
        useAuthStore.getState().logout();
        return Promise.reject(errorToProcess);
      } finally {
        isRefreshing = false;
      }
    },
  );
}
