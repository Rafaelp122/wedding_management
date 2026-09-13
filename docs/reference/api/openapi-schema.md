# Especificação Técnica: Endpoints e Schemas OpenAPI

> **Módulo:** [api-reference](index.md) | [system-overview](../../architecture/concepts/system-overview.md)
> **Camada:** Backend (`backend/apps/api.py`, `routers/`)

---

## Visão Geral

A API do **Wedding Management System** é desenvolvida com **Django Ninja**, oferecendo digitação estrita via Pydantic, geração automática de especificação OpenAPI 3.0 e integração assíncrona com o frontend.

---

## Mapeamento de Routers e `operation_id`

Conforme padronizado na arquitetura (ADR-012), todos os endpoints utilizam o atributo obrigatório `operation_id` para permitir que o **Orval** gere os hooks TypeScript fortemente tipados no frontend.

| Router | Prefixo | Descrição | `operation_id` Principal |
| :--- | :--- | :--- | :--- |
| `auth` | `/api/v1/auth/` | Cadastro, login JWT, OAuth2, redefinição e verificação de e-mail | `auth_register_user`, `auth_obtain_token`, `auth_password_reset_request`, `auth_password_reset_confirm`, `auth_verify_email`, `auth_resend_verification` |
| `weddings` | `/api/v1/weddings/` | Gestão de casamentos e membros | `weddings_list`, `weddings_create`, `weddings_retrieve` |
| `finances` | `/api/v1/finances/` | Orçamentos, categorias, despesas e parcelas | `finances_budgets_list`, `finances_expenses_create` |
| `logistics` | `/api/v1/logistics/` | Fornecedores, contratos e itens | `logistics_suppliers_list`, `logistics_contracts_create` |
| `scheduler` | `/api/v1/scheduler/` | Cronogramas, eventos e tarefas | `scheduler_events_list`, `scheduler_tasks_create` |
| `tenants` | `/api/v1/tenants/` | Gestão do tenant/empresa e convites | `tenants_company_retrieve` |

---

## Autenticação e Headers

- **Header de Autenticação:** `Authorization: Bearer <access_token>`
- **Header de Multi-tenancy:** O tenant é identificado automaticamente através do token JWT do usuário autenticado (`user.company_id`).

## Endpoints de Recuperação e Verificação

| Endpoint | Finalidade | Resposta de erro relevante |
| :--- | :--- | :--- |
| `POST /api/v1/auth/password-reset/request/` | Solicita o envio de instruções para redefinir a senha. | Resposta genérica para evitar enumeração de e-mails. |
| `POST /api/v1/auth/password-reset/confirm/` | Valida `uid` + token e salva a nova senha. | `invalid_token` ou `invalid_password`. |
| `POST /api/v1/auth/verify-email/` | Confirma o e-mail e ativa a conta. | `invalid_token`. |
| `POST /api/v1/auth/resend-verification/` | Reenvia o link para uma conta não verificada. | Resposta genérica e throttle anônimo. |

Os fluxos de token usam o `default_token_generator` do Django. Os endpoints públicos possuem throttles específicos e não expõem a existência de contas.

---

## Estrutura dos Schemas Pydantic

### Response Schema Padrão (200 OK)
As respostas de sucesso retornam diretamente os schemas serializados do Pydantic ou coleções paginadas.

```json
{
  "id": 12,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "title": "Casamento Ana & Pedro",
  "wedding_date": "2026-11-20",
  "created_at": "2026-07-27T00:00:00Z"
}
```

### Schema de Paginação
```json
{
  "count": 42,
  "items": [...]
}
```
