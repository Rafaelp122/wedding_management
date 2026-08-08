---
title: "Regras de Integridade Financeira"
domain: finances
type: business-rule
code: backend/apps/finances/services/expense_service.py
tests: backend/apps/finances/tests/services/test_expense_service.py
---

# Regra de Negócio: Integridade Contábil e Regras Financeiras

> **Módulo:** [finances-domain](../../domains/finances-domain.md) | [expense-model](../../../3-reference/models/finances/expense-model.md)
> **Código:** `backend/apps/finances/services/expense_service.py`, `backend/apps/finances/services/installment_service.py`
> **Testes:** `backend/apps/finances/tests/services/test_expense_service.py`

---

## 1. Imutabilidade e Proteção Contábil (`models.PROTECT`)

No gerenciamento financeiro de eventos, o dinheiro efetivamente gasto ou comprometido é um fato histórico.

- A entidade `Expense` protege a sua categoria orçamentária (`BudgetCategory`) utilizando a chave estrangeira `models.PROTECT`.
- **Efeito:** Impede que uma categoria com despesas ativas seja excluída fisicamente, garantindo que parcelas (`Installment`) nunca fiquem órfãs e mantendo o histórico de gastos reais do casamento.

---

## 2. Regras de Negócio de Despesas e Parcelas

### BR-F02 — Conformidade Contratual
Quando uma despesa é criada ou atualizada a partir de um contrato (`Contract`), o valor real da despesa (`expense.actual_amount`) **deve ser estritamente igual** ao valor total do contrato (`contract.total_amount`). Tentativas de divergência disparam `BusinessRuleViolation` (`br_f02_violation`).

### BR-F03 — Fronteira de Casamento (Cross-Wedding Guard)
O contrato vinculado a uma despesa deve pertencer obrigatoriamente ao mesmo casamento (`wedding_id`) da categoria orçamentária. Divergências disparam `DomainIntegrityError` (`expense_contract_wedding_mismatch`).

### BR-F04 — Bloqueio de Alteração por Pagamento Efetuado
Se existirem parcelas com status `PAID` vinculadas a uma despesa:
- É **estritamente proibido** alterar o valor total da despesa (`actual_amount`).
- É **estritamente proibido** redistribuir o número de parcelas.
- Tentativas de alteração disparam `BusinessRuleViolation` (`amount_change_blocked_by_paid`).

### BR-F05 — Invariante Cronológica no Ajuste de Parcelas
Ao ajustar a data de vencimento de uma parcela (`InstallmentService.adjust`):
- A nova data de vencimento **não pode ser anterior** ao vencimento da parcela imediatamente anterior (`due_date_before_previous_installment`).
- A nova data de vencimento **não pode ser posterior** ao vencimento da parcela imediatamente seguinte (`due_date_after_next_installment`).
