export {};

/**
 * Estende `InternalAxiosRequestConfig` do Axios com o flag `_retry`
 * usado pelo interceptor de auth-refresh para evitar loops infinitos
 * de renovação de token.
 */
declare module "axios" {
  export interface InternalAxiosRequestConfig {
    _retry?: boolean;
  }
}
