/**
 * Padrão de erro do Django Rest Framework e da sua Service Layer
 */
export interface DjangoErrorResponse {
  // Erros gerais (ex: "Token inválido" ou "Erro de integridade")
  detail?: string;

  // Erros de validação do DRF (ex: { "bride_name": ["Este campo é obrigatório"] })
  // O record permite qualquer nome de campo que venha do seu Serializer
  [key: string]: string | string[] | undefined;

  // Para caso a Service Layer retorne um formato customizado para 422/409
  message?: string;
  code?: string;
}
