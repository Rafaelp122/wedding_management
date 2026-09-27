"""Módulo de schemas para o domínio de agendamento e tarefas (Scheduler)."""

from apps.scheduler.schemas.event import (
    EventIn,
    EventOut,
    EventPatchIn,
    EventUpdateIn,
    SchedulerSummaryOut,
)
from apps.scheduler.schemas.task import (
    ChecklistItemIn,
    ChecklistItemOut,
    ChecklistItemPatchIn,
    TaskIn,
    TaskOut,
    TaskPatchIn,
    TimelineCompressionOut,
)


__all__ = [
    "ChecklistItemIn",
    "ChecklistItemOut",
    "ChecklistItemPatchIn",
    "EventIn",
    "EventOut",
    "EventPatchIn",
    "EventUpdateIn",
    "SchedulerSummaryOut",
    "TaskIn",
    "TaskOut",
    "TaskPatchIn",
    "TimelineCompressionOut",
]
