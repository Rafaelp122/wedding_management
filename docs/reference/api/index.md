# Especificações da API REST (OpenAPI 3.1 & Django Ninja)

> **Categoria:** Referência Técnica (API & Contratos)
> **Relacionados:** [ADR-013: Migração para Django Ninja](../../architecture/adr/013-migrate-drf-to-ninja.md) · [ADR-012: Orval Contract-Driven Frontend](../../architecture/adr/012-orval-contract-driven-frontend.md) · [Query Selectors](../architecture-standards/query-selectors-spec.md)

---

## 1. Visão Geral da Arquitetura de API

A API REST do **Wedding Management System** é construída com **Django Ninja** e **Pydantic v2**, expondo contratos fortemente tipados em conformidade estrita com a especificação **OpenAPI 3.1**.

### Características Centrais
- **Autenticação Global JWT:** Todos os endpoints exigem Bearer JWT (`auth=JWTAuth()`), exceto rotas públicas explicitamente desprotegidas (`/health`, `/auth/login`, `/auth/register`).
- **Geração Automatizada de Clientes:** O schema JSON (`/api/v1/openapi.json`) serve de entrada única para o gerador de código **Orval**, que compila hooks React Query e tipos TypeScript para o frontend.
- **Isolamento CQRS:** Rotas `GET` invocam seletores em `selectors/`, enquanto mutações (`POST`, `PUT`, `PATCH`, `DELETE`) executam serviços em `services/`.
- **Roteamento Previsível:** Roteadores desacoplados registrados sob o prefixo `/api/v1/`.

```mermaid
flowchart LR
    Client["Frontend SPA (React 19 / Orval)"] -->|HTTPS Bearer JWT| NinjaAPI["Django Ninja Router (/api/v1/)"]
    NinjaAPI -->|GET Query| Selectors["Query Selectors (selectors/)"]
    NinjaAPI -->|Mutations| Services["Service Layer (services/)"]
    Selectors -->|Tenant QuerySet| DB[(PostgreSQL Neon)]
    Services -->|@transaction.atomic| DB
    NinjaAPI -.->|Export| OpenAPISpec["OpenAPI 3.1 Schema (openapi.json)"]
    OpenAPISpec -.->|Generate Hooks| OrvalGen["Orval Code Generator"]
```

---

## 2. Convenções Normativas de Rotas

1. **Prefixo Global:** Todas as rotas de negócio residem sob `/api/v1/`.
2. **Identificador Único (`operation_id`):** Obrigatório em 100% dos endpoints. Segue o padrão `<dominio>_<entidade>_<acao>` (ex: `weddings_list`, `finances_expenses_create`, `logistics_contracts_upload_url`).
3. **Ordenação de Rotas (ADR-022):** Rotas estáticas literais (ex: `/upload-url/`, `/lookup/`, `/by-month/`) DEVEM ser declaradas antes de rotas dinâmicas parametrizadas (ex: `/{uuid:uuid}/`).
4. **Tipagem de Parâmetros de Caminho:** Parâmetros de UUID devem ser tipados com `uuid: UUID4` ou no formato Ninja `/{uuid:uuid}/`.

---

## 3. Mapeamento de Tags e Domínios da API

| Tag OpenAPI | Prefixo de Rota | Arquivo de Rota | Responsabilidade de Domínio |
| :--- | :--- | :--- | :--- |
| `Weddings` | `/api/v1/weddings/` | `apps/weddings/api.py` | Gestão central de casamentos, status e convidados. |
| `Finances` | `/api/v1/finances/` | `apps/finances/api/` | Orçamentos, categorias, despesas e parcelas financeiras. |
| `Logistics` | `/api/v1/logistics/` | `apps/logistics/api/` | Fornecedores, contratos logísticos e itens/serviços. |
| `Scheduler` | `/api/v1/scheduler/` | `apps/scheduler/api/` | Eventos do cronograma, checklist e tarefas operacionais. |
| `Reporting` | `/api/v1/dashboard/`, `/api/v1/reports/` | `apps/reporting/api.py` | Métricas agregadas, painel executivo e relatórios. |
| `Auth` | `/api/v1/auth/` | `apps/users/api.py` | Login JWT, registro, refresh token e recuperação de senha. |
| `Notifications` | `/api/v1/notifications/` | `apps/notifications/api.py` | Notificações do sistema e alertas em tempo real. |
| `Core` | `/api/v1/health`, `/api/v1/internal/cron/` | `config/api.py`, `core/cron_api.py` | Health check de infraestrutura e disparo de jobs agendados. |

---

## 4. Padrões de Resposta e Envelopes

### 4.1 Respostas de Sucesso
- **`200 OK`:** Consultas de leitura única e atualizações (`PATCH`, `PUT`).
- **`201 Created`:** Criação de novos registros (`POST`).
- **`204 No Content`:** Remoção de registros (`DELETE`) com body vazio.

### 4.2 Respostas Paginadas (`PaginationResponseSchema`)
Listagens utilizam o decorador `@paginate` do Django Ninja:
```json
{
  "count": 42,
  "items": [
    {
      "uuid": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "name": "Casamento Maria & João",
      "date": "2026-11-20"
    }
  ]
}
```

### 4.3 Envelopes de Erro Padronizados (`ErrorResponseSchema`)
Todos os erros seguem a especificação de envelope consistente tratada em `config/api.py`:
```json
{
  "detail": "Orçamento ultrapassou o teto estipulado.",
  "code": "business_rule_violation"
}
```

---

## 5. Documentos nesta Seção (Notas Atômicas)

- :material-code-json: **[openapi-schema.md](openapi-schema.md)** — Especificação e exportação do schema OpenAPI 3.1.
- :material-alert-circle-outline: **[error-envelope-spec.md](error-envelope-spec.md)** — Padronização de códigos de erro HTTP e handlers da API.
