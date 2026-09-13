# Domínio de Tenants (Empresas & Multi-Tenancy)

> **Categoria:** Domínios de Arquitetura (Bounded Contexts)
> **Relacionados:** [ADR-009: Multi-Tenancy](../adr/009-multitenancy.md) · [ADR-016: Multi-Tenancy Pragmático](../adr/016-pragmatic-multi-tenancy.md) · [ADR-019: Validação de Tenant na Service Layer](../adr/019-tenant-validation-service-layer.md) · [Estratégia de Multi-Tenancy](../concepts/multi-tenancy-strategy.md) · [Modelos Base & Padrões Core](../../reference/models/core-models.md) · [Core Domain](core-domain.md)

---

## 1. Visão Geral do Domínio

O domínio de **Tenants** é responsável por garantir a segregação lógica e o isolamento absoluto de dados entre as diferentes assessorias de eventos, cerimoniais e noivos (*self-service*) que utilizam a plataforma.

A arquitetura adota a estratégia de **Multi-Tenancy Pragmático** (ADR-009 / ADR-016):
- Um único banco de dados compartilhado (Neon PostgreSQL) com particionamento lógico em nível de linha (*Row-Level Isolation* via chave estrangeira `company_id`).
- Todas as entidades de negócio herdam de `TenantModel`, que injeta a chave estrangeira obrigatória para `Company` e vincula o `TenantManager`.
- Todas as leituras e mutações exigem a passagem explícita do objeto `Company` vindo da autenticação (`request.user.company`).
- Provisionamento automatizado do workspace com slug anti-colisão e workspace reservado para superusuários (`admin-workspace`).

---

## 2. Diagrama ERD de Relacionamento Multi-Tenant

```mermaid
erDiagram
    Company ||--o{ User : "possui (PROTECT)"
    Company ||--o{ Wedding : "gerencia (CASCADE)"
    Company ||--o{ Supplier : "cadastra (CASCADE)"
    Company ||--o{ Contract : "formaliza (CASCADE)"
    Company ||--o{ Budget : "orça (CASCADE)"
    Company ||--o{ BudgetCategory : "agrupa (CASCADE)"
    Company ||--o{ Expense : "compromete (CASCADE)"
    Company ||--o{ Installment : "parcela (CASCADE)"
    Company ||--o{ Event : "agenda (CASCADE)"
    Company ||--o{ Task : "executa (CASCADE)"
    Company ||--o{ Notification : "notifica (CASCADE)"

    Company {
        bigint id PK
        uuid uuid UK "Identificador Público"
        string name "Nome da Assessoria / Empresa"
        string slug UK "Identificador único na URL"
        boolean is_active "Status de Ativação"
        datetime created_at
        datetime updated_at
    }

    TenantModel {
        bigint id PK
        uuid uuid UK
        bigint company_id FK "Company (Tenant Owner)"
        datetime created_at
        datetime updated_at
    }
```

---

## 3. Tabela de Entidades e Invariantes de Persistência

| Entidade / Componente | Papel Arquitetural | Campos & Chaves | Invariantes de Persistência & Regras de Isolamento |
| :--- | :--- | :--- | :--- |
| **`Company`** | Agregado Raiz do Tenant | `id` (bigint PK), `uuid` (UUID4 único), `name` (max 255), `slug` (unique, indexado), `is_active` (boolean, default True) | **Anti-Colisão:** O slug é gerado a partir do nome com sufixo UUID de 8 caracteres (`slugify(name)[:40] + '-' + uuid[:8]`).<br/>**Workspace Administrativo:** O slug `admin-workspace` é reservado exclusivamente para superusuários e tarefas de sistema. |
| **`TenantModel`** | Modelo Base Abstrato | `company` (`ForeignKey` para `Company`, `on_delete=models.CASCADE`), `objects = TenantManager()` | **Isolamento de Linha:** Todo modelo filho é forçado a ter `company_id`.<br/>**Índice Composto:** Possui índice `["company", "uuid"]` para garantir lookups $O(1)$ filtrados por tenant.<br/>**Manager Customizado:** Utiliza `TenantManager` que expõe `.for_tenant(company)`. |
| **`TenantQuerySet`** | Camada de Consulta Segura | Método `.for_tenant(company: Company)` | **Filtro Estrito:** Aplica `self.filter(company=company)` no nível do QuerySet Django, prevenindo consultas vazadas entre empresas distintas. |
| **`TenantService`** | Orquestrador de Mutação | `create_company()`, `get_or_create_admin_workspace()` | **Transação Atômica:** Executa a criação da empresa em bloco `@transaction.atomic`. Chamado de forma transparente durante o fluxo de registro do usuário (`RegistrationService`). |

---

## 4. Transclusão de Código Real

### A. Definição do Modelo `Company` e `TenantModel`
```python
--8<-- "backend/apps/tenants/models.py:7:48"
```

### B. Manager e QuerySet de Isolamento (`TenantQuerySet`)
```python
--8<-- "backend/apps/tenants/managers.py:14:32"
```

### C. Serviço de Provisionamento de Tenants (`TenantService`)
```python
--8<-- "backend/apps/tenants/services/tenant_service.py:13:65"
```

### D. Seletor de Busca Segura de Empresa (`company_get_selector`)
```python
--8<-- "backend/apps/tenants/selectors.py:13:28"
```

---

## 5. Mapeamento de Camadas (Fullstack)

### Camada de Backend (`backend/apps/tenants/`)
- **Modelos:** `Company` (`companies`) e `TenantModel` abstrato em `models.py`.
- **Managers:** `TenantManager` e `TenantQuerySet` em `managers.py`.
- **Services:** `TenantService.create_company` e `TenantService.get_or_create_admin_workspace` em `services/tenant_service.py`.
- **Selectors:** `company_get_selector` em `selectors.py`.

### Camada de Frontend (`frontend/src/`)
- **Store de Autenticação:** `useAuthStore` armazena a empresa ativa (`Company`) do usuário logado.
- **Injeção de Header e Contexto:** O cliente Axios (`src/api/client.ts`) anexa as credenciais JWT que codificam o `company_id` e validam o tenant em cada requisição.

---

## 6. Links e Referências Cruzadas

- [Estratégia de Multi-Tenancy](../concepts/multi-tenancy-strategy.md)
- [ADR-009: Multi-Tenancy](../adr/009-multitenancy.md)
- [ADR-016: Multi-Tenancy Pragmático](../adr/016-pragmatic-multi-tenancy.md)
- [ADR-019: Validação de Tenant na Service Layer](../adr/019-tenant-validation-service-layer.md)
- [Modelos Base & Padrões Core](../../reference/models/core-models.md)
- [Users Domain](users-domain.md)
