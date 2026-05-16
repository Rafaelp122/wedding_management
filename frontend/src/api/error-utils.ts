import { AxiosError } from "axios";

import type { DjangoErrorResponse } from "@/api/types/backend";
import type { ApiErrorInfo } from "@/api/types/errors";

const STATUS_MESSAGES: Record<number, string> = {
  401: "Sua sessão expirou. Faça login novamente.",
  403: "Você não tem permissão para executar esta ação.",
  409: "Conflito de dados. Atualize a página e tente novamente.",
  422: "Alguns dados enviados são inválidos. Revise e tente novamente.",
};

/**
 * Extrai o primeiro erro de campo voltado ao usuário de um payload de erro
 * Django/DRF. Ignora chaves reservadas (`detail`, `message`, `code`) que
 * já são tratadas em nível superior. Suporta tanto erros de campo como
 * array (`["msg"]`) quanto como string simples.
 */
function firstFieldError(payload: DjangoErrorResponse): string | undefined {
  for (const [key, value] of Object.entries(payload)) {
    if (key === "detail" || key === "message" || key === "code") {
      continue;
    }

    if (Array.isArray(value) && value.length > 0) {
      return String(value[0]);
    }

    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }

  return undefined;
}

/**
 * Extrai uma mensagem de erro legível e um código de status opcional de um
 * erro de API (tipicamente um `AxiosError` com corpo Django/DRF).
 *
 * Ordem de resolução:
 * 1. `payload.detail`
 * 2. `payload.message`
 * 3. Primeiro erro de campo não-reservado (suporta arrays e strings)
 * 4. Mensagem de fallback baseada no status HTTP (401, 403, 409, 422)
 * 5. String `fallback` fornecida pelo chamador
 *
 * Para erros não-Axios (ex.: falha de rede, strings lançadas) a mensagem
 * de fallback é usada diretamente.
 */
export function getApiErrorInfo(
  error: unknown,
  fallback = "Não foi possível concluir a operação.",
): ApiErrorInfo {
  if (!(error instanceof AxiosError)) {
    return { message: fallback };
  }

  const status = error.response?.status;
  const payload = (error.response?.data ?? {}) as DjangoErrorResponse;

  const message =
    payload.detail ||
    payload.message ||
    firstFieldError(payload) ||
    (status ? STATUS_MESSAGES[status] : undefined) ||
    fallback;

  return {
    status,
    code: payload.code,
    message,
  };
}
