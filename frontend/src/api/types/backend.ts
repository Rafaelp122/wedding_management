/**
 * Formato da resposta de erro retornada pela API Django Rest Framework /
 * Django Ninja. Acomoda tanto erros genéricos (`detail`, `message`, `code`)
 * quanto erros de validação por campo (ex.: `{ bride_name: ["Obrigatório"] }`).
 */
export interface DjangoErrorResponse {
  detail?: string;
  [key: string]: string | string[] | undefined;
  message?: string;
  code?: string;
}
