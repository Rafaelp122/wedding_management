import type { PydanticValidationItem } from "./errors";

/**
 * Formato da resposta de erro retornada pela API Django Ninja.
 *
 * Acomoda três formatos distintos:
 * 1. Erros de domínio (ApplicationError): `{ detail: string, code: string }`
 * 2. Erros de validação Pydantic (422): `{ detail: PydanticValidationItem[] }`
 * 3. Erros de campo convencionais: `{ field_name: string[], ... }`
 */
export interface DjangoErrorResponse {
  detail?: string | PydanticValidationItem[];
  message?: string;
  code?: string;
  [key: string]: string | string[] | PydanticValidationItem[] | undefined;
}
