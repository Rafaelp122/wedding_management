---
title: "Referência do Modelo: BudgetCategory"
domain: finances
type: model-reference
code: backend/apps/finances/models/budget_category.py
tests: backend/apps/finances/tests/categories/test_models.py
---

# Referência do Modelo: BudgetCategory

> **Módulo:** [finances-domain](../../../architecture/domains/finances-domain.md) | [budget-category-distribution](../../../architecture/business-rules/finances/budget-category-distribution.md)
> **Código:** `backend/apps/finances/models/budget_category.py`, `backend/apps/finances/managers.py`
> **Testes:** `backend/apps/finances/tests/categories/test_models.py`

---

## Estrutura do Modelo `BudgetCategory`

Herda de `TenantModel` e `WeddingOwnedMixin`. Alocação orçamentária por categoria (ex: Buffet, Decoração, Foto & Vídeo).

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `budget`: `ForeignKey` (`finances.Budget`, `on_delete=CASCADE`, `related_name="categories"`).
- `name`: `CharField(max_length=100)`.
- `allocated_budget`: `DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])`.
- `description`: `TextField(blank=True)`.

### Restrições:
- `unique_together`: `[["budget", "name"]]` — Impede categorias duplicadas no mesmo orçamento.

---

## Otimizações do Manager (`BudgetCategoryQuerySet.with_total_spent`)

O `BudgetCategoryManager` implementa o método `with_total_spent()`, que anota a propriedade `_total_spent` calculando a soma das parcelas com status `PAID` diretamente na query SQL.

### Properties:
- `total_spent`: Retorna a anotação `_total_spent` ou executa uma agregação SQL secundária.
