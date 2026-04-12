from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.models import BaseModel
from apps.users.models import User


class Task(BaseModel, WeddingOwnedMixin):
    """Modelo que representa um item no checklist do casamento."""

    planner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="task_records"
    )

    title = models.CharField(max_length=255, verbose_name="Título da Tarefa")
    description = models.TextField(blank=True, verbose_name="Descrição detalhada")
    due_date = models.DateField(null=True, blank=True, verbose_name="Prazo Estimado")
    is_completed = models.BooleanField(default=False, verbose_name="Concluída?")

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["is_completed", "due_date", "created_at"]
        indexes = [
            models.Index(fields=["planner", "is_completed"]),
            models.Index(fields=["wedding", "is_completed"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        status = "[x]" if self.is_completed else "[ ]"
        return f"{status} {self.title}"
