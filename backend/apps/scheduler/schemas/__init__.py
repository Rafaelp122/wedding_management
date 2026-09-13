"""Módulo de schemas para o domínio de agendamento e tarefas (Scheduler)."""

from apps.scheduler.schemas.event import (
    EventIn,
    EventOut,
    EventPatchIn,
)
from apps.scheduler.schemas.task import (
    TaskIn,
    TaskOut,
    TaskPatchIn,
)


__all__ = [
    "EventIn",
    "EventOut",
    "EventPatchIn",
    "TaskIn",
    "TaskOut",
    "TaskPatchIn",
]
