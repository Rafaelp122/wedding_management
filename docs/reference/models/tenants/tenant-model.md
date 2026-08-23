---
title: "Modelo de Tenant (Company)"
domain: tenants
type: model-reference
code: backend/apps/tenants/models.py
tests: backend/apps/tenants/tests/test_models.py
---

# Referência do Modelo: Company & TenantModel

> **Módulo:** [tenants-domain](../../../architecture/domains/tenants-domain.md) | [multi-tenancy-strategy](../../../architecture/concepts/multi-tenancy-strategy.md)
> **Código:** `backend/apps/tenants/models.py`, `backend/apps/tenants/managers.py`

---

## 1. `Company` (Tenant Root — Tabela `companies`)

Representa a empresa, assessoria de eventos ou o casal cadastrado no sistema.

### Campos:
- `name`: `CharField(max_length=255)` — Nome da empresa.
- `is_active`: `BooleanField(default=True)` — Status ativo da empresa no sistema.
- `slug`: `SlugField(unique=True)` — Identificador único na URL (gerado com sufixo UUID anti-colisão pelo `TenantService`).

---

## 2. `TenantModel` (Classe Base Abstrata)

Modelo base abstrato para todas as entidades que pertencem a um Tenant. Garante o isolamento estrito de dados por empresa.

### Campos:
- `company`: `ForeignKey("tenants.Company", on_delete=models.CASCADE, related_name="%(class)s_records")`.

### Índices de Performance:
- `models.Index(fields=["company", "uuid"])` — Índice composto que otimiza buscas por empresa e chave primária UUID no PostgreSQL.

---

## 3. Gerenciador de Banco (`TenantManager` / `TenantQuerySet`)

Fornece o método `.for_tenant(company)`. **Atenção:** A filtragem por tenant não é aplicada automaticamente no `.all()`; ela exige a invocação explícita de `.for_tenant(company)` no QuerySet para garantir o isolamento:

```python
# Exemplo de uso
weddings = Wedding.objects.for_tenant(company)
```
