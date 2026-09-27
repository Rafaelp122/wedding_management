# Integridade e Auditoria Financeira

> **Aviso de Fonte Única da Verdade (SSOT):**
> A documentação canônica de regras financeiras segue o padrão Diátaxis e reside exclusivamente em:
> - [`docs/architecture/business-rules/finances/financial-integrity-rules.md`](../../../../docs/architecture/business-rules/finances/financial-integrity-rules.md)
> - [`docs/architecture/business-rules/finances/budget-category-distribution.md`](../../../../docs/architecture/business-rules/finances/budget-category-distribution.md)
> - [`docs/architecture/business-rules/finances/installment-overdue-logic.md`](../../../../docs/architecture/business-rules/finances/installment-overdue-logic.md)

---

## 1. Imutabilidade Contábil e Proteção Relacional

1. **Expense (on_delete=models.PROTECT):**
   - A despesa (`Expense`) protege sua categoria via `models.PROTECT`.
   - Impede que qualquer processo remova uma categoria que possua compromissos financeiros vinculados (`category_protected_error`).
   - Garante que cada parcela (`Installment`) mantenha vínculo estrito com sua despesa e categoria.

2. **Conservação de Teto Orçamentário (`BR-F04`):**
   - A soma de todas as categorias alocadas (`allocated_budget`) não pode exceder o teto estimado do orçamento (`total_estimated`), com verificação garantida em `BudgetCategory.clean()` e lock pessimista no service.

3. **Paridade Contrato-Despesa (`BR-F02`):**
   - Toda despesa vinculada a contrato deve ter valor estritamente idêntico ao valor total do contrato, garantido no model `Expense.clean()`.

4. **Imutabilidade de Parcela Paga (`BR-F06`):**
   - Parcelas com status `PAID` não podem ter seu valor, data de vencimento ou número alterados, garantido no model `Installment.clean()`.
