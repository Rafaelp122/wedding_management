import Axios, { AxiosError, type AxiosInstance } from "axios";
import type { InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/stores/authStore";
import { normalizeError } from "@/api/utils/normalize-error";
import { createQueue } from "@/api/utils/queue-manager";

/**
 * Reenvia uma requisição que estava na fila aguardando o refresh do token.
 *
 * Verifica novamente o sinal de abort — cobre a race condition em que
 * `AbortController.abort()` é chamado entre a resolução da fila e a
 * execução efetiva do retry.
 */
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

/**
 * Chama o endpoint de refresh, persiste os novos tokens via callback,
 * resolve as requisições enfileiradas e reenvia a requisição original
 * com o access token atualizado.
 */
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

/**
 * Registra um interceptor de resposta que renova access tokens expirados
 * de forma transparente.
 *
 * Fluxo:
 * 1. Erros não-401 e requisições já reenviadas passam direto.
 * 2. 401s concorrentes durante um refresh ativo entram na fila e são
 *    reenviados quando o novo token chega.
 * 3. O primeiro 401 dispara um POST para `/api/v1/auth/refresh/`. Em caso
 *    de sucesso, os tokens são persistidos, a fila é drenada e a requisição
 *    original é reenviada. Em caso de falha, todas as requisições da fila
 *    são rejeitadas e o usuário é deslogado.
 *
 * O estado (`isRefreshing`, `queue`) pertence ao closure — cada instância
 * Axios recebe o seu próprio via `createAxiosInstance()`.
 */
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

      const isLoginRequest = originalRequest.url?.includes("/auth/token/");
      if (
        error.response?.status !== 401 ||
        originalRequest._retry ||
        isLoginRequest
      ) {
        return Promise.reject(error);
      }

      if (isRefreshing) {
        originalRequest._retry = true;
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
