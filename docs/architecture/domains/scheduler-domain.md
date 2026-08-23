# MOC de Domínio: Scheduler (Agenda, Cronograma e Checklist)

> **Hub de Domínio:** [scheduler-domain](scheduler-domain.md) | [system-overview](../concepts/system-overview.md)
> **Camadas Mapeadas:** `backend/apps/scheduler/` & `frontend/src/features/scheduler/`

---

## Visão Geral do Domínio

O domínio de **Scheduler** é o coração da organização temporal do evento. Gerencia a agenda interativa de compromissos, o cronograma/timeline de marcos e o checklist operacional de tarefas do casamento.

---

## Mapeamento de Camadas (Fullstack)

### 1. Camada de Backend (`backend/apps/scheduler/`)
- **Modelos de Dados:**
  - [event-model](../../reference/models/scheduler/event-model.md): Compromissos e marcos na agenda.
  - [task-model](../../reference/models/scheduler/task-model.md): Itens do checklist operacional.
- **Service Layer:** `events.py`, `tasks.py`, `templates.py`.

### 2. Camada de Frontend (`frontend/src/features/scheduler/`)
- **Páginas & Views:**
  - `SchedulerPage.tsx` — Página unificada com navegação por abas.
  - `SchedulerCalendar.tsx` — Calendário interativo de compromissos.
  - `TimelineView.tsx` & `TimelineTable.tsx` — Visão em linha do tempo dos marcos do evento.
  - `ChecklistView.tsx` & `ChecklistTable.tsx` — Tabela interativa de tarefas do checklist.
- **Componentes Visuais & Dialogs:**
  - `SchedulerSummaryCards.tsx` — Cards de resumo de compromissos.
  - `ReadOnlyEventDetails.tsx` — Componente somente leitura para exibição de eventos de pagamento.
  - `CreateEventDialog.tsx`, `EditEventDialog.tsx` — Gestão de compromissos.
- **Hooks Customizados:** `useSchedulerPage.ts`, `useTimeline.ts`, `useChecklist.ts`, `useCreateEventForm.ts`, `useEditEventForm.ts`.

---

## Regras de Negócio Associadas
- [recurrence-rules-engine](../business-rules/scheduler/recurrence-rules-engine.md): Motor de recorrência de eventos.
- [payment-event-readonly-guard](../business-rules/scheduler/payment-event-readonly-guard.md): Proteção de imutabilidade dos eventos do tipo pagamento (BR-S01) e trava de data inicial no passado (BR-S02).
- [wedding-schedule-templates](../business-rules/weddings/wedding-schedule-templates.md): Geração automática de cronograma a partir de templates.
