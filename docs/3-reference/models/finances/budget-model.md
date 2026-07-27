# Referência do Modelo: Budget

> **Módulo:** [finances-domain](../../../4-explanation/domains/finances-domain.md) | [budget-category-distribution](../../../4-explanation/business-rules/finances/budget-category-distribution.md)
> **Código:** `backend/apps/finances/models/budget.py`, `backend/apps/finances/managers.py`

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
