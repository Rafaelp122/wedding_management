from django.db import models

from apps.core.models import BaseModel
from apps.events.mixins import EventOwnedMixin
from apps.tenants.mixins import CompanyOwnedMixin


class Task(BaseModel, CompanyOwnedMixin, EventOwnedMixin):
    """Modelo que representa um item no checklist do casamento."""

    title = models.CharField(max_length=255, verbose_name="Título da Tarefa")
    description = models.TextField(  # noqa: DJ001
        null=True, blank=True, verbose_name="Descrição detalhada"
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Prazo Estimado")
    is_completed = models.BooleanField(default=False, verbose_name="Concluída?")

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["is_completed", "due_date", "created_at"]
        indexes = [
            models.Index(fields=["company", "is_completed"]),
            models.Index(fields=["event", "is_completed"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        status = "[x]" if self.is_completed else "[ ]"
        return f"{status} {self.title}"
