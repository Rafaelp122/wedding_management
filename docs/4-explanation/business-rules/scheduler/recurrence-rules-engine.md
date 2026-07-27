# Regra de Negócio: Motor de Recorrência e Agendamentos

> **Módulo:** [scheduler-domain](../../domains/scheduler-domain.md) | [event-model](../../../3-reference/models/scheduler/event-model.md) | [task-model](../../../3-reference/models/scheduler/task-model.md)
> **Código:** `backend/apps/scheduler/services/scheduler_service.py`

---

## 1. Conflito de Horários em Eventos

- Não é permitido agendar dois eventos simultâneos para o mesmo casamento no mesmo intervalo de `start_time` e `end_time`.

---

## 2. Prazos e Priorização de Tarefas

- Tarefas com `priority='URGENT'` cuja `due_date` seja inferior a 7 dias da data atual são automaticamente destacadas na visão do dashboard do assessor.
