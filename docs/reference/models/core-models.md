---
title: "Modelos Core e Mixins"
domain: core
type: model-reference
code: backend/apps/core/models.py
tests: backend/apps/core/tests/test_base_model.py
---

# Referência do Modelo: Core (Base Models & Mixins)

> **Módulo:** [core-domain](../../architecture/domains/core-domain.md) | [multi-tenancy-strategy](../../architecture/concepts/multi-tenancy-strategy.md)
> **Código:** `backend/apps/core/models.py`, `backend/apps/core/mixins.py`

---

## 1. `BaseModel`

Modelo abstrato base herdado por todas as entidades do sistema (`backend/apps/core/models.py`).

### Campos:
- `id`: `BigAutoField` (Primary Key).
- `uuid`: `UUIDField` (`default=uuid.uuid4`, `editable=False`, `unique=True`, `db_index=True`) — Identificador público seguro consumido pela API.
- `created_at`: `DateTimeField` (`auto_now_add=True`) — Timestamp de criação.
- `updated_at`: `DateTimeField` (`auto_now=True`) — Timestamp da última modificação.

### Métodos e Comportamento:
- **`full_clean()` no `save()` (ADR-011):** Executa obrigatoriamente as validações do modelo antes de salvar no banco. Pode ser ignorado temporariamente via `save(skip_clean=True)`.
- **`get_by_uuid(uuid_str)`:** Método estático utilitário para busca rápida por UUID.

---

## 2. `WeddingOwnedMixin`

Mixin abstrato (`backend/apps/core/mixins.py`) para entidades que pertencem a um casamento específico.

### Campos:
- `wedding`: `ForeignKey` (`weddings.Wedding`, `on_delete=CASCADE`, `related_name="%(class)s_records"`).

### Validação `clean()`:
- Garante a integridade multi-tenant: se o modelo for um `TenantModel`, valida se `wedding.company_id == company_id`.
