# MOC de Domínio: Tenants (Empresas e Multi-Tenancy)

> **Hub de Domínio:** [tenants-domain](tenants-domain.md) | [multi-tenancy-strategy](../concepts/multi-tenancy-strategy.md)
> **Camadas Mapeadas:** `backend/apps/tenants/` & `frontend/src/stores/`

---

## Visão Geral do Domínio

O domínio de **Tenants** provê a infraestrutura de isolamento multi-tenant por empresa/assessoria de eventos.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/tenants/`)
- **Modelos de Dados:**
  - [tenant-model](../../reference/models/tenants/tenant-model.md): Modelo `Company` (`companies`) e a classe base abstrata `TenantModel`.
- **Managers:** `TenantManager` e `TenantQuerySet` com o método `.for_tenant(company)`. Veja [multi-tenancy-strategy](../concepts/multi-tenancy-strategy.md).
- **Service Layer (`tenant_service.py`):**
  - `create_company`: Criação atômica de empresa com geração de slug anti-colisão (`slugify(display_name)[:40] + '-' + uuid[:8]`).
  - `get_or_create_admin_workspace`: Provisionamento do `admin-workspace` para associação segura de superusuários e tarefas de gerenciamento global.

### 2. Camada de Frontend (`frontend/src/`)
- **Store de Sessão:** `useAuthStore` contendo a `Company` ativa do usuário autenticado. Veja [store-state-spec](../../reference/frontend/store-state-spec.md).
- **Header HTTP / Interceptor Axios:** Injeção do contexto do tenant ativo em todas as chamadas API para o backend.

---

## Regras de Negócio Associadas
- [multi-tenancy-strategy](../concepts/multi-tenancy-strategy.md): Estratégia de isolamento por empresa.
