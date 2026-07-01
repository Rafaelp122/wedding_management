import { AxiosError } from "axios";
import type { UseFormSetError, FieldValues, Path } from "react-hook-form";

import type { DjangoErrorResponse } from "@/api/types/backend";
import type { ApiErrorInfo, PydanticValidationItem } from "@/api/types/errors";

const STATUS_MESSAGES: Record<number, string> = {
  401: "Sua sessão expirou. Faça login novamente.",
  403: "Você não tem permissão para executar esta ação.",
  409: "Conflito de dados. Atualize a página e tente novamente.",
  422: "Alguns dados enviados são inválidos. Revise e tente novamente.",
};

/**
 * Extrai o primeiro erro de campo voltado ao usuário de um payload de erro
 * Django Ninja. Ignora chaves reservadas (`detail`, `message`, `code`) que
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
 * erro de API (tipicamente um `AxiosError` com corpo Django Ninja).
 *
 * Ordem de resolução:
 * 1. `payload.detail` (se for string ou primeiro erro se for array)
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
    if (error instanceof Error && error.message) {
      return { message: error.message };
    }
    if (typeof error === "string" && error.trim()) {
      return { message: error };
    }
    return { message: fallback };
  }

  if (error.message === "Network Error" || !error.response) {
    return {
      message: "Não foi possível conectar ao servidor. Por favor, tente novamente mais tarde.",
    };
  }

  const status = error.response?.status;
  const payload = (error.response?.data ?? {}) as DjangoErrorResponse;

  let detailMessage: string | undefined;
  if (typeof payload.detail === "string") {
    detailMessage = payload.detail;
  } else if (Array.isArray(payload.detail) && payload.detail.length > 0) {
    const firstErr: PydanticValidationItem | undefined = payload.detail[0];
    if (firstErr && typeof firstErr === "object" && "loc" in firstErr) {
      const field = firstErr.loc.length > 0 ? firstErr.loc[firstErr.loc.length - 1] : "";
      detailMessage = field && field !== "body" ? `${field}: ${firstErr.msg}` : firstErr.msg;
    }
  }

  const message =
    detailMessage ||
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

/**
 * Mapeia erros de validação retornados pela API diretamente para os campos
 * correspondentes do formulário no React Hook Form.
 * Retorna true se algum erro foi mapeado.
 */
export function mapErrorsToForm<T extends FieldValues>(
  error: unknown,
  setError: UseFormSetError<T>
): boolean {
  if (!(error instanceof AxiosError) || !error.response) {
    return false;
  }

  const payload = error.response.data as DjangoErrorResponse;
  if (!payload) return false;

  let hasSetErrors = false;

  // 1. Erros de validação do Django Ninja (Pydantic / status 422)
  if (Array.isArray(payload.detail)) {
    for (const err of payload.detail) {
      if (err && typeof err === "object" && "loc" in err) {
        const validationErr: PydanticValidationItem = err;
        if (Array.isArray(validationErr.loc)) {
          const fieldName = validationErr.loc[validationErr.loc.length - 1];
          if (fieldName && fieldName !== "body") {
            setError(fieldName as Path<T>, {
              type: "server",
              message: validationErr.msg || "Erro de validação",
            });
            hasSetErrors = true;
          }
        }
      }
    }
  }

  // 2. Erros de campo convencionais (ex: { email: ["msg"] })
  for (const [key, value] of Object.entries(payload)) {
    if (key === "detail" || key === "message" || key === "code") {
      continue;
    }

    let errorMessage = "";
    if (Array.isArray(value) && value.length > 0) {
      errorMessage = String(value[0]);
    } else if (typeof value === "string") {
      errorMessage = value;
    }

    if (errorMessage) {
      setError(key as Path<T>, {
        type: "server",
        message: errorMessage,
      });
      hasSetErrors = true;
    }
  }

  return hasSetErrors;
}
