from django.db import models
from django.utils import timezone

from apps.core.mixins import WeddingOwnedMixin
from apps.scheduler.managers import TaskQuerySet
from apps.tenants.models import TenantModel


class Task(TenantModel, WeddingOwnedMixin):
    """Modelo que representa um item no checklist do casamento."""

    objects = TaskQuerySet.as_manager()  # type: ignore[assignment,misc]

    title = models.CharField(max_length=255, verbose_name="Título da Tarefa")
    description = models.TextField(blank=True, verbose_name="Descrição detalhada")
    due_date = models.DateField(null=True, blank=True, verbose_name="Prazo Estimado")
    is_completed = models.BooleanField(default=False, verbose_name="Concluída?")

    class Meta:
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ["is_completed", "due_date", "created_at"]
        indexes = [
            models.Index(fields=["company", "is_completed"]),
            models.Index(fields=["wedding", "is_completed"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self) -> str:
        status = "[x]" if self.is_completed else "[ ]"
        return f"{status} {self.title}"

    # ── Métodos Semânticos de Ciclo de Vida ──────────────────────────────

    def complete(self) -> None:
        """Marca a tarefa como concluída."""
        self.is_completed = True

    def reopen(self) -> None:
        """Reabre a tarefa previamente concluída."""
        self.is_completed = False

    # ── Propriedades Semânticas ──────────────────────────────────────────

    @property
    def is_overdue(self) -> bool:
        """Indica se a tarefa não concluída já ultrapassou o prazo de vencimento."""
        return (
            not self.is_completed
            and self.due_date is not None
            and self.due_date < timezone.localdate()
        )

    @property
    def days_overdue(self) -> int:
        """Quantidade de dias de atraso caso a tarefa esteja atrasada."""
        return (
            (timezone.localdate() - self.due_date).days
            if (self.is_overdue and self.due_date)
            else 0
        )
