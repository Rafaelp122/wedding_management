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

## 4. Implementação no Código-Fonte Real

- **Modelos de Isolamento:** [`Company`](../../../backend/apps/tenants/models.py) e [`TenantModel`](../../../backend/apps/tenants/models.py)
- **Manager e QuerySet Especializado:** [`TenantQuerySet`](../../../backend/apps/tenants/managers.py) e [`TenantManager`](../../../backend/apps/tenants/managers.py)
- **Serviço de Provisionamento:** [`TenantService`](../../../backend/apps/tenants/services/tenant_service.py)
- **Seletor de Consulta:** [`company_get_selector()`](../../../backend/apps/tenants/selectors.py)

### A. Definição do Modelo `Company` e `TenantModel`

```python
class Company(BaseModel):
    name = models.CharField("Nome da Empresa", max_length=255)
    is_active = models.BooleanField("Ativa", default=True)
    slug = models.SlugField(unique=True, help_text="Identificador único na URL")

    class Meta:
        db_table = "companies"

class TenantModel(BaseModel):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="%(class)s_records")
    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["company", "uuid"]),
        ]
```

### B. Manager e QuerySet de Isolamento (`TenantQuerySet`)

```python
class TenantQuerySet(models.QuerySet[_ModelT]):
    def for_tenant(self, company: Company) -> Self:
        return self.filter(company=company)

class TenantManager(models.Manager[_ModelT]):
    _queryset_class = TenantQuerySet

    def get_queryset(self) -> TenantQuerySet[_ModelT]:
        return self._queryset_class(self.model, using=self._db)

    def for_tenant(self, company: Company) -> TenantQuerySet[_ModelT]:
        return self.get_queryset().for_tenant(company)
```

### C. Serviço de Provisionamento de Tenants (`TenantService`)

```python
class TenantService:
    @staticmethod
    @transaction.atomic
    def create_company(display_name: str, company_name: str = "") -> Company:
        name = company_name.strip() if company_name else f"Workspace de {display_name}"
        base_slug = slugify(display_name)[:40]
        unique_slug = f"{base_slug}-{str(uuid_lib.uuid4())[:8]}"
        return Company.objects.create(name=name, slug=unique_slug, is_active=True)

    @staticmethod
    @transaction.atomic
    def get_or_create_admin_workspace() -> Company:
        company, _ = Company.objects.get_or_create(
            slug="admin-workspace", defaults={"name": "Workspace Administrativo"}
        )
        return company
```

### D. Seletor de Busca Segura de Empresa (`company_get_selector`)

```python
def company_get_selector(*, uuid: UUID | str) -> Company:
    company = Company.objects.filter(uuid=uuid).first()
    if not company:
        raise ObjectNotFoundError(detail="Empresa não encontrada.")
    return company
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
