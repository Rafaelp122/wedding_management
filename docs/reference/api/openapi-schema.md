# Especificação Técnica: Endpoints e Schemas OpenAPI

> **Categoria:** Referência Técnica (API & Contratos)
> **Relacionados:** [Hub de APIs](index.md) · [Envelope de Erros](error-envelope-spec.md) · [ADR-012: Orval Contract-Driven Frontend](../../architecture/adr/012-orval-contract-driven-frontend.md) · [ADR-013: Migração para Django Ninja](../../architecture/adr/013-migrate-drf-to-ninja.md)

---

## 1. Visão Geral

A API do **Wedding Management System** é desenvolvida com **Django Ninja**, oferecendo tipagem estrita via Pydantic v2, geração automática de especificação OpenAPI 3.1 e integração tipada de ponta a ponta com o frontend via Orval.

---

## 2. Mapeamento de Routers e `operation_id`

Conforme padronizado na arquitetura (ADR-012), todos os endpoints utilizam o atributo obrigatório `operation_id` para permitir que o **Orval** gere os hooks TypeScript fortemente tipados no frontend.

| Router | Prefixo | Descrição | `operation_id` Principal / Operações Suportadas |
| :--- | :--- | :--- | :--- |
| `auth` | `/api/v1/auth/` | Cadastro, login JWT, OAuth2, redefinição e verificação de e-mail | `auth_register_user`, `auth_obtain_token`, `auth_password_reset_request`, `auth_password_reset_confirm`, `auth_verify_email`, `auth_resend_verification` |
| `weddings` | `/api/v1/weddings/` | Gestão de casamentos, comboboxes, métricas mensais e ciclo de vida | `weddings_list`, `weddings_create`, `weddings_read`, `weddings_update`, `weddings_delete`, `weddings_lookup`, `weddings_by_month`, `weddings_complete`, `weddings_cancel`, `weddings_reopen` |
| `dashboard` | `/api/v1/dashboard/` | Métricas operacionais, KPIs agregados do tenant, fluxo de caixa e progresso | `dashboard_summary`, `dashboard_wedding`, `dashboard_chart_cash_flow`, `dashboard_chart_task_progress`, `dashboard_operations_list` |
| `reports` | `/api/v1/reports/` | Exportação de relatórios analíticos consolidados (PDF e planilhas Excel) | `reports_wedding_export` |
| `finances` | `/api/v1/finances/` | Orçamentos mestre, categorias, despesas e parcelas financeiras | `finances_budgets_list`, `finances_budgets_create`, `finances_categories_list`, `finances_expenses_create`, `finances_installments_list` |
| `logistics` | `/api/v1/logistics/` | Fornecedores, contratos, itens/serviços e upload direto ao Cloudflare R2 | `logistics_suppliers_list`, `logistics_contracts_list`, `logistics_contracts_create_full`, `logistics_contracts_upload_url`, `logistics_items_list` |
| `scheduler` | `/api/v1/scheduler/` | Cronograma de eventos, checklist de casamento e tarefas operacionais | `scheduler_events_list`, `scheduler_events_create`, `scheduler_tasks_list`, `scheduler_tasks_create` |
| `notifications` | `/api/v1/notifications/` | Gestão de notificações in-app, contagem pendente e mutações em lote | `notifications_list`, `notifications_unread_count`, `notifications_mark_all_as_read`, `notifications_bulk_mark_as_read`, `notifications_bulk_delete` |
| `tenants` | `/api/v1/tenants/` | Gestão do tenant/empresa e configurações da organização | `tenants_company_retrieve` |
| `cron` | `/api/v1/internal/cron/` | Jobs de automação disparados pelo Google Cloud Scheduler via OIDC | `cron_mark_overdue_installments`, `cron_send_payment_reminders` |

---

## 3. Autenticação e Headers

- **Header de Autenticação:** `Authorization: Bearer <access_token>`
- **Header de Multi-tenancy:** O tenant é identificado automaticamente através do token JWT do usuário autenticado (`user.company_id`), prevenindo vazamento de dados entre empresas.

### Endpoints de Recuperação e Verificação de Conta

| Endpoint | Finalidade | Resposta de erro relevante |
| :--- | :--- | :--- |
| `POST /api/v1/auth/password-reset/request/` | Solicita o envio de instruções para redefinir a senha. | Resposta genérica para evitar enumeração de e-mails. |
| `POST /api/v1/auth/password-reset/confirm/` | Valida `uid` + token e salva a nova senha. | `invalid_token` ou `invalid_password`. |
| `POST /api/v1/auth/verify-email/` | Confirma o e-mail e ativa a conta. | `invalid_token`. |
| `POST /api/v1/auth/resend-verification/` | Reenvia o link para uma conta não verificada. | Resposta genérica e throttle anônimo. |

Os fluxos de token usam o `default_token_generator` do Django. Os endpoints públicos possuem throttles específicos e não expõem a existência de contas.

---

## 4. Estrutura dos Schemas Pydantic

### Response Schema Canônico de Casamento (`WeddingOut`)
As respostas de sucesso serializam o schema completo de domínio, incluindo invariantes calculadas e transições permitidas na máquina de estados:

```json
{
  "uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
  "groom_name": "Pedro Santos",
  "bride_name": "Ana Oliveira",
  "date": "2026-11-20",
  "location": "Espaço das Flores, São Paulo - SP",
  "expected_guests": 150,
  "status": "IN_PROGRESS",
  "template": "standard_wedding",
  "created_at": "2026-07-27T10:00:00Z",
  "updated_at": "2026-07-27T10:00:00Z",
  "total_budget": 85000.0,
  "overdue_installments": 0,
  "incomplete_tasks": 4,
  "allowed_transitions": [
    "COMPLETED",
    "CANCELED"
  ],
  "can_complete": true
}
```

### Schema de Paginação Padrão
Endpoints de listagem decorados com `@paginate` retornam a contagem e coleção de registros:
```json
{
  "count": 42,
  "items": [
    {
      "uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab",
      "groom_name": "Pedro Santos",
      "bride_name": "Ana Oliveira",
      "date": "2026-11-20",
      "location": "Espaço das Flores, São Paulo - SP",
      "status": "IN_PROGRESS"
    }
  ]
}
```
