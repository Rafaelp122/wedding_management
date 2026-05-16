import type { AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/authStore";

/**
 * Registra um interceptor de requisição que anexa o Bearer token atual
 * da store Zustand de autenticação em todas as requisições. Se não houver
 * token (usuário não autenticado), a requisição é enviada sem o header
 * Authorization.
 */
export function addAuthRequestInterceptor(instance: AxiosInstance) {
  instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      const token = useAuthStore.getState().accessToken;
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error),
  );
}
