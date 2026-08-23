---
title: "Referência do Modelo: Installment"
domain: finances
type: model-reference
code: backend/apps/finances/models/installment.py
tests: backend/apps/finances/tests/installments/test_models.py
---

# Referência do Modelo: Installment

> **Módulo:** [finances-domain](../../../architecture/domains/finances-domain.md) | [installment-overdue-logic](../../../architecture/business-rules/finances/installment-overdue-logic.md)
> **Código:** `backend/apps/finances/models/installment.py`
> **Testes:** `backend/apps/finances/tests/installments/test_models.py`

---

## Estrutura do Modelo `Installment`

Herda de `TenantModel`. Representa uma parcela individual de pagamento de uma despesa.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `expense`: `ForeignKey` (`finances.Expense`, `on_delete=CASCADE`, `related_name="installments"`).
- `installment_number`: `PositiveIntegerField()` — Número de ordem da parcela.
- `amount`: `DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])`.
- `due_date`: `DateField()` — Data de vencimento.
- `paid_date`: `DateField(null=True, blank=True)` — Data de confirmação de pagamento.
- `status`: `CharField(max_length=20, choices=StatusChoices, default='PENDING')`:
  - `PENDING` ("Pendente")
  - `PAID` ("Pago")
  - `OVERDUE` ("Atrasado")
- `notes`: `TextField(blank=True)`.

### Restrições:
- `unique_together`: `[["expense", "installment_number"]]`.

### Validações do `clean()`:
- Garante coerência entre `status` e `paid_date`: se `status == PAID`, `paid_date` é obrigatório; se `status != PAID`, `paid_date` deve ser nulo.
