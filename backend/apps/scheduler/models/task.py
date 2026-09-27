import datetime as dt

from django.db import models
from django.utils import timezone

from apps.core.mixins import WeddingOwnedMixin
from apps.scheduler.managers import TaskQuerySet
from apps.tenants.models import TenantModel


class ChecklistItem(TenantModel, WeddingOwnedMixin):
    """Modelo que representa um item no checklist operacional do casamento (RF-18)."""

    objects = TaskQuerySet.as_manager()  # type: ignore[assignment,misc]

    class PriorityChoices(models.TextChoices):
        LOW = "LOW", "Baixa"
        MEDIUM = "MEDIUM", "Média"
        HIGH = "HIGH", "Alta"
        URGENT = "URGENT", "Urgente"

    title = models.CharField(max_length=255, verbose_name="Título da Tarefa")
    description = models.TextField(blank=True, verbose_name="Descrição detalhada")
    due_date = models.DateField(null=True, blank=True, verbose_name="Prazo Estimado")
    priority = models.CharField(
        max_length=20,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
        verbose_name="Prioridade",
    )
    is_completed = models.BooleanField(default=False, verbose_name="Concluída?")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Data de Conclusão",
    )

    class Meta:
        db_table = "scheduler_task"
        verbose_name = "Item de Checklist"
        verbose_name_plural = "Itens de Checklist"
        ordering = ["is_completed", "due_date", "created_at"]
        indexes = [
            models.Index(fields=["company", "is_completed"]),
            models.Index(fields=["wedding", "is_completed"]),
            models.Index(fields=["due_date"]),
            models.Index(fields=["company", "priority"]),
        ]

    def __str__(self) -> str:
        status = "[x]" if self.is_completed else "[ ]"
        return f"{status} {self.title}"

    # ── Métodos Semânticos de Ciclo de Vida ──────────────────────────────

    def complete(self) -> None:
        """Marca a tarefa como concluída e registra o timestamp."""
        self.is_completed = True
        self.completed_at = timezone.now()

    def reopen(self) -> None:
        """Reabre a tarefa previamente concluída e limpa o timestamp."""
        self.is_completed = False
        self.completed_at = None

    def update_details(
        self,
        *,
        title: str | None = None,
        description: str | None = None,
        due_date: dt.date | None = None,
        priority: str | None = None,
    ) -> None:
        """Atualiza os dados cadastrais da tarefa.

        Args:
            title: Novo título opcional.
            description: Nova descrição opcional.
            due_date: Novo prazo estimado opcional.
            priority: Nova prioridade opcional.
        """
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if due_date is not None:
            self.due_date = due_date
        if priority is not None:
            self.priority = priority

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


# Alias canônico para manter retrocompatibilidade com importações anteriores (ADR-031 / RFC-001)
Task = ChecklistItem
