# Especificação Técnica: Envelope de Erros da API (Django Ninja)

> **Módulo:** [api-reference](index.md) | [system-overview](../../4-explanation/architecture/system-overview.md)
> **Camada:** Backend (`backend/apps/core/exceptions.py`, `backend/apps/api.py`)

---

## Visão Geral

O Django Ninja centraliza a captura de exceções através do custom exception handler em `backend/apps/core/exceptions.py`. Todas as respostas de erro HTTP (códigos 4xx e 5xx) seguem um envelope JSON estritamente padronizado.

---

## Envelope Padrão de Erro

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Erro de validação nos campos informados.",
    "details": {
      "email": ["Este campo é obrigatório."]
    }
  }
}
```

---

## Códigos de Erro Mapeados (`code`)

| Código HTTP | Code | Exceção Origem | Descrição |
| :--- | :--- | :--- | :--- |
| `400 Bad Request` | `VALIDATION_ERROR` | `django.core.exceptions.ValidationError` | Erro disparado por `full_clean()` nos models ou validações de formulário. |
| `401 Unauthorized` | `UNAUTHENTICATED` | `NinjaJWTException` / `AuthenticationError` | Token ausente, expirado ou inválido. |
| `403 Forbidden` | `PERMISSION_DENIED` | `PermissionDenied` | Usuário sem acesso ao tenant ou recurso solicitado. |
| `404 Not Found` | `NOT_FOUND` | `Http404` / `ObjectDoesNotExist` | Recurso não localizado para o tenant atual. |
| `422 Unprocessable` | `INVALID_PAYLOAD` | `pydantic.ValidationError` | Erro nos tipos ou estrutura do body recebido. |
| `500 Server Error` | `INTERNAL_SERVER_ERROR` | Exceção genérica não tratada | Falha interna no servidor (mascarando detalhes em produção). |

---

## Integração com Frontend

O Axios no frontend intercepta o envelope de erro através do interceptor global em `src/api/client.ts`. Os erros de validação (`VALIDATION_ERROR`) são automaticamente propagados para o `react-hook-form` exibindo as mensagens diretamente nos inputs.
