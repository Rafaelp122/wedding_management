import type { InternalAxiosRequestConfig } from "axios";

/**
 * Requisição diferida aguardando a conclusão de um refresh de token.
 * `resolve`/`reject` controlam o destino da promise que o interceptor
 * retornou ao chamador original; `config` carrega o contexto da requisição
 * (incluindo o sinal de abort) para o reenvio.
 */
export interface FailedQueueItem {
  resolve: (token: string) => void;
  reject: (error: Error) => void;
  config: InternalAxiosRequestConfig;
}
