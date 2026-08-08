---
title: "Referência do Modelo: Expense"
domain: finances
type: model-reference
code: backend/apps/finances/models/expense.py
tests: backend/apps/finances/tests/expenses/test_models.py
---

# Referência do Modelo: Expense

> **Módulo:** [finances-domain](../../../4-explanation/domains/finances-domain.md) | [installment-overdue-logic](../../../4-explanation/business-rules/finances/installment-overdue-logic.md) | [financial-integrity-rules](../../../4-explanation/business-rules/finances/financial-integrity-rules.md)
> **Código:** `backend/apps/finances/models/expense.py`, `backend/apps/finances/managers.py`
> **Testes:** `backend/apps/finances/tests/expenses/test_models.py`

---

## Estrutura do Modelo `Expense`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa uma despesa ou compromisso financeiro vinculado a um casamento.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `wedding`: `ForeignKey` (`weddings.Wedding`, `on_delete=CASCADE`).
- `category`: `ForeignKey` (`finances.BudgetCategory`, `on_delete=PROTECT`, `related_name="expenses"`).
- `contract`: `OneToOneField` (`logistics.Contract`, `null=True`, `blank=True`, `on_delete=SET_NULL`, `related_name="expense"`).
- `description`: `TextField` — Descrição detalhada da despesa.
- `estimated_amount`: `DecimalField(max_digits=10, decimal_places=2, default=0.00)` — Valor orçado.
- `actual_amount`: `DecimalField(max_digits=10, decimal_places=2, default=0.00)` — Valor real contratado.
- `due_date`: `DateField(null=True, blank=True)` — Data de vencimento base.
- `notes`: `TextField(blank=True)`.

---

## Otimizações do Manager (`ExpenseQuerySet.with_details`)

O `ExpenseManager` implementa o método customizado `with_details()`, que anota cada despesa da lista em uma única consulta SQL otimizada:
- `installments_count`: Contagem total de parcelas.
- `paid_installments_count`: Contagem de parcelas com `status="PAID"`.
- `total_paid`: Soma dos valores de parcelas `PAID`.
- `total_pending`: Soma dos valores de parcelas `PENDING` ou `OVERDUE`.

---

## Validações do `clean()` (Tolerância Zero - ADR-010):
- Valida se a soma das parcelas registradas em `Installment` é exatamente igual a `actual_amount`.
