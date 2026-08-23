---
title: "Modelo de Item Contratado"
domain: logistics
type: model-reference
code: backend/apps/logistics/models/item.py
tests: backend/apps/logistics/tests/items/test_models.py
---

# Referência do Modelo: Item

> **Módulo:** [logistics-domain](../../../architecture/domains/logistics-domain.md) | [contract-parent-child-hierarchy](../../../architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
> **Código:** `backend/apps/logistics/models/item.py`

---

## Estrutura do Modelo `Item`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa cada item ou serviço individual especificado em um contrato.

### Campos:
- `company`: ForeignKey (`tenants.Company`)
- `wedding`: ForeignKey (`weddings.Wedding`)
- `contract`: ForeignKey (`logistics.Contract`, on_delete=CASCADE, related_name="items")
- `name`: CharField(max_length=255)
- `quantity`: PositiveIntegerField(default=1)
- `unit_price`: DecimalField(max_digits=12, decimal_places=2)
- `total_price`: DecimalField(max_digits=12, decimal_places=2)
