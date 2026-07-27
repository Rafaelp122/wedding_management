# Regra de Negócio: Distribuição e Alocação por Categoria de Orçamento

> **Módulo:** [finances-domain](../../domains/finances-domain.md) | [budget-model](../../../3-reference/models/finances/budget-model.md) | [budget-category-model](../../../3-reference/models/finances/budget-category-model.md)
> **Código:** `backend/apps/finances/services/budget_service.py`

---

## 1. Teto Orçamentário e Categorização

- A soma das `allocated_amount` de todas as `BudgetCategory` atreladas a um `Budget` não deve ultrapassar o `total_amount` do orçamento do casamento.
- Quando uma nova `Expense` é adicionada a uma categoria, o serviço valida se o teto alocado da categoria é respeitado. Se ultrapassado, um aviso de estouro de categoria é gerado.

---

## 2. Cálculo do Gráfico de Distribuição no Frontend

As porcentagens de alocação e gasto real por categoria são calculadas através de funções puras no frontend (`src/features/finances/utils/chartHelpers.ts`), permitindo testes unitários síncronos com Vitest.
