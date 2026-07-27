# Referência do Modelo: Task

> **Módulo:** [scheduler-domain](../../../4-explanation/domains/scheduler-domain.md) | [recurrence-rules-engine](../../../4-explanation/business-rules/scheduler/recurrence-rules-engine.md)
> **Código:** `backend/apps/scheduler/models/task.py`

---

## Estrutura do Modelo `Task`

Herda de `TenantModel` e `WeddingOwnedMixin`. Representa uma tarefa ou item de checklist do cronograma.

### Campos:
- `company`: `ForeignKey` (`tenants.Company`).
- `wedding`: `ForeignKey` (`weddings.Wedding`, `on_delete=CASCADE`).
- `title`: `CharField(max_length=200)` — Título da tarefa.
- `description`: `TextField(blank=True)` — Descrição detalhada.
- `due_date`: `DateField(null=True, blank=True)` — Data limite para execução.
- `is_completed`: `BooleanField(default=False)` — Indicador de conclusão.
