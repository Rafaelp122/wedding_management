export interface DjangoErrorResponse {
  detail?: string;
  [key: string]: string | string[] | undefined;
  message?: string;
  code?: string;
}
