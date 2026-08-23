---
title: "Referência do Modelo: Budget"
domain: finances
type: model-reference
code: backend/apps/finances/models/budget.py
tests: backend/apps/finances/tests/budgets/test_models.py
---

# Referência do Modelo: Budget

> **Módulo:** [finances-domain](../../../architecture/domains/finances-domain.md) | [budget-category-distribution](../../../architecture/business-rules/finances/budget-category-distribution.md)
> **Código:** `backend/apps/finances/models/budget.py`, `backend/apps/finances/managers.py`
> **Testes:** `backend/apps/finances/tests/budgets/test_models.py`

---

## Estrutura do Modelo `Budget`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa o orçamento global consolidado de um casamento.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `wedding`: `OneToOneField` (`weddings.Wedding`, `on_delete=CASCADE`, `related_name="budget"`).
- `total_estimated`: `DecimalField(max_digits=10, decimal_places=2, default=0.00, validators=[MinValueValidator(0)])` — Teto orçamentário total.
- `notes`: `TextField(blank=True)`.

---

## Otimizações do Manager (`BudgetQuerySet.with_total_spent`)

O `BudgetManager` implementa o método `with_total_spent()`, que executa um `annotate()` SQL anotando a propriedade `_total_overall_spent` com a soma das parcelas efetivamente pagas (`status="PAID"`) em todas as categorias do casamento.

### Properties:
- `total_overall_spent`: Retorna a anotação `_total_overall_spent` ou executa a agregação no banco.
