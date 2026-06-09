/**
 * Formato de erro normalizado consumido pelos componentes de UI. Produzido
 * por `getApiErrorInfo()` a partir de um erro bruto da API.
 */
export interface ApiErrorInfo {
  status?: number;
  code?: string;
  message: string;
}

/**
 * Erro de validação individual retornado pelo Django Ninja (Pydantic).
 * Formato: `{ type, loc, msg }` — status 422.
 */
export interface PydanticValidationItem {
  type: string;
  loc: (string | number)[];
  msg: string;
  input?: unknown;
}
