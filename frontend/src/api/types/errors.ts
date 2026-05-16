/**
 * Formato de erro normalizado consumido pelos componentes de UI. Produzido
 * por `getApiErrorInfo()` a partir de um erro bruto da API.
 */
export interface ApiErrorInfo {
  status?: number;
  code?: string;
  message: string;
}
