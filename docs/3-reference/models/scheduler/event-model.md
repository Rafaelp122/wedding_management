---
title: "Referência do Modelo: Event"
domain: scheduler
type: model-reference
code: backend/apps/scheduler/models/event.py
tests: backend/apps/scheduler/tests/appointments/test_models.py
---

# Referência do Modelo: Event

> **Módulo:** [scheduler-domain](../../../4-explanation/domains/scheduler-domain.md) | [recurrence-rules-engine](../../../4-explanation/business-rules/scheduler/recurrence-rules-engine.md) | [payment-event-readonly-guard](../../../4-explanation/business-rules/scheduler/payment-event-readonly-guard.md)
> **Código:** `backend/apps/scheduler/models/event.py`
> **Testes:** `backend/apps/scheduler/tests/appointments/test_models.py`

---

## Estrutura do Modelo `Event`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa compromissos e marcos na agenda do casamento.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `wedding`: `ForeignKey` (`weddings.Wedding`, `on_delete=CASCADE`).
- `title`: `CharField(max_length=255)` — Título do evento.
- `location`: `CharField(max_length=255, blank=True)` — Local do compromisso.
- `description`: `TextField(blank=True)`.
- `event_type`: `CharField(max_length=50)` — Enum `TypeChoices`:
  - `reuniao` ("Reunião")
  - `pagamento` ("Pagamento" — Read-only gerado pelo financeiro)
  - `visita` ("Visita Técnica")
  - `degustacao` ("Degustação")
  - `outro` ("Outro")
- `start_time`: `DateTimeField` — Data e hora de início.
- `end_time`: `DateTimeField(null=True, blank=True)` — Data e hora de término.
- `recurrence_rule`: `CharField(max_length=20)` — Enum `RecurrenceChoices`:
  - `none` ("Não recorrente")
  - `semanal` ("Semanal")
  - `quinzenal` ("Quinzenal")
  - `mensal` ("Mensal")
- `reminder_enabled`: `BooleanField(default=False)` — Ativação de lembrete.
- `reminder_minutes_before`: `PositiveIntegerField(default=60)` — Minutos de antecedência do aviso.
- `source_installment`: `ForeignKey("finances.Installment", on_delete=SET_NULL, null=True, blank=True)` — Parcela de origem para eventos de pagamento.
