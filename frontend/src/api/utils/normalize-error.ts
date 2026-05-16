import Axios, { AxiosError } from "axios";

/**
 * Normaliza um throwable desconhecido em `Error` ou `AxiosError`.
 *
 * - AxiosError → retornado como está.
 * - Error → retornado como está.
 * - Qualquer outro tipo (string, number, null, undefined, etc.) →
 *   encapsulado em `new Error(String(err))` para que o código downstream
 *   sempre receba um objeto Error válido.
 */
export function normalizeError(err: unknown): AxiosError | Error {
  if (Axios.isAxiosError(err)) return err;
  if (err instanceof Error) return err;
  return new Error(String(err));
}
