# MOC de Domínio: Finances (Gestão Financeira e Orçamentária)

> **Hub de Domínio:** [finances-domain](finances-domain.md) | [system-overview](../concepts/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/finances/` & `frontend/src/features/finances/`

---

## Visão Geral do Domínio

O domínio de **Finances** gerencia todo o ciclo orçamentário do casamento, desde o planejamento do teto orçamentário até a distribuição por categorias, cadastro de despesas e controle de parcelamentos.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/finances/`)
- **Modelos de Dados:**
  - [budget-model](../../reference/models/finances/budget-model.md): Orçamento global do casamento.
  - [budget-category-model](../../reference/models/finances/budget-category-model.md): Alocação por categorias (Buffet, Decoração, etc.).
  - [expense-model](../../reference/models/finances/expense-model.md): Compromisso financeiro ou contrato.
  - [installment-model](../../reference/models/finances/installment-model.md): Parcelamento de pagamentos com datas de vencimento.
- **Service Layer:** `budget_service.py`, `expense_service.py`, `installment_service.py`. Veja [service-layer-pattern](../concepts/service-layer-pattern.md).
- **Management Command:** `python manage.py mark_overdue_installments` para atualizar status de parcelas. Veja [installment-overdue-logic](../business-rules/finances/installment-overdue-logic.md).

### 2. Camada de Frontend (`frontend/src/features/finances/`)
- **Containers & Views:**
  - `FinancesView.tsx` — Conteiner visual principal de finanças.
  - `ExpensesTab.tsx` — Conteiner da aba de despesas.
  - `ExpensesTable.tsx` — Tabela visual de despesas.
  - `ExpenseDetailSheet.tsx` & `ExpenseDetailSheetPresenter.tsx` — Painel lateral de detalhes da despesa.
  - `FinancesSummaryCards.tsx` & `FinancesDistributionChart.tsx` — Cards e gráfico de distribuição com Recharts.
- **Dialogs de Manutenção:**
  - `CreateExpenseDialog.tsx`, `EditExpenseDialog.tsx`, `DeleteExpenseDialog.tsx` — Gestão de despesas.
  - `CreateBudgetCategoryDialog.tsx`, `EditBudgetCategoryDialog.tsx` — Gestão de categorias.
- **Hooks Customizados:** `useBudget.ts`, `useExpenses.ts`, `useCreateExpenseForm.ts`, `useEditExpenseForm.ts`.

---

## Regras de Negócio Associadas
- [installment-overdue-logic](../business-rules/finances/installment-overdue-logic.md): Cálculo de parcelas (Tolerância Zero) e transição para `OVERDUE`.
- [financial-integrity-rules](../business-rules/finances/financial-integrity-rules.md): Regras de integridade contábil BR-F02 a BR-F05 (`models.PROTECT`, conformidade contratual e invariante cronológica).
- [payment-schedule-integration](../business-rules/finances/payment-schedule-integration.md): Regra BR-S01 de auto-geração de eventos de pagamento na agenda do Scheduler.
- [budget-category-distribution](../business-rules/finances/budget-category-distribution.md): Validação de estouro de categoria e distribuição orçamentária.
