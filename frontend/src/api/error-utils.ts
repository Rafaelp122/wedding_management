import { AxiosError } from "axios";

import type { DjangoErrorResponse } from "@/types/api";

export interface ApiErrorInfo {
  status?: number;
  code?: string;
  message: string;
}

const STATUS_MESSAGES: Record<number, string> = {
  401: "Sua sessão expirou. Faça login novamente.",
  403: "Você não tem permissão para executar esta ação.",
  409: "Conflito de dados. Atualize a página e tente novamente.",
  422: "Alguns dados enviados são inválidos. Revise e tente novamente.",
};

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
