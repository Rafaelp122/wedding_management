import type { AxiosInstance, AxiosResponse } from "axios";
import * as Sentry from "@sentry/react";
import { toast } from "sonner";

/**
 * Interceptador de resposta global para capturar falhas críticas de infraestrutura,
 * como quedas de conexão, timeouts ou servidores offline (502, 503, 504).
 *
 * Também propaga o X-Request-ID do backend para o Sentry como contexto,
 * permitindo correlacionar erros frontend com logs backend.
 *
 * Utiliza o parâmetro `id` do toast da biblioteca Sonner para evitar a
 * sobreposição/acumulação de múltiplos alertas em chamadas simultâneas.
 */
export function addConnectionErrorInterceptor(instance: AxiosInstance) {
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      const requestId = response.headers["x-request-id"];
      if (requestId) {
        Sentry.setContext("request", { request_id: requestId });
      }
      return response;
    },
    (error) => {
      const requestId = error.response?.headers?.["x-request-id"];
      if (requestId) {
        Sentry.setContext("request", { request_id: requestId });
      }

      const isConnectionError =
        error.message === "Network Error" ||
        error.code === "ERR_NETWORK" ||
        (error.response && [502, 503, 504].includes(error.response.status));

      if (isConnectionError) {
        toast.error("Não foi possível conectar ao servidor. Por favor, tente novamente mais tarde.", {
          id: "network-error",
        });

        Sentry.captureException(error, {
          tags: { source: "connection-error-interceptor" },
        });
      }

      return Promise.reject(error);
    },
  );
}
