from __future__ import annotations

from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation
from apps.tenants.models import TenantModel
from apps.weddings.managers import WeddingQuerySet


def validate_future_date(value: date) -> None:
    """Validador auxiliar para verificar se a data informada não está no passado."""
    if value < timezone.now().date():
        raise ValidationError("A data do casamento não pode ser no passado.")


class Wedding(TenantModel):
    """
    Agregado central que representa um evento de casamento no sistema.

    Encapsula o ciclo de vida do planejamento, máquina de estados de transição,
    invariantes de data e template de cronograma.
    """

    objects = WeddingQuerySet.as_manager()  # type: ignore[assignment,misc]

    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        StatusChoices.IN_PROGRESS.value: [
            StatusChoices.COMPLETED.value,
            StatusChoices.CANCELED.value,
        ],
        StatusChoices.CANCELED.value: [
            StatusChoices.IN_PROGRESS.value,
        ],
        StatusChoices.COMPLETED.value: [],
    }

    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    expected_guests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Convidados",
        help_text="Quantidade estimada de convidados",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )
    template = models.CharField(  # noqa: DJ001
        max_length=50,
        null=True,
        blank=True,
        verbose_name="Modelo de Cronograma",
        help_text="Template aplicado na criação do casamento",
    )

    class Meta:
        verbose_name = "Casamento"
        verbose_name_plural = "Casamentos"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.groom_name} & {self.bride_name}"

    # ── Regras de Domínio e Invariantes (Nível 2) ─────────────────────────

    def clean(self) -> None:
        """Valida invariantes de integridade e consistência direta do modelo."""
        super().clean()
        today = timezone.now().date()
        if (
            self._state.adding
            and self.status == self.StatusChoices.IN_PROGRESS
            and self.date
            and self.date < today
        ):
            raise ValidationError(
                {"date": "A data do casamento não pode ser no passado."}
            )
        if (
            self.status == self.StatusChoices.COMPLETED
            and self.date
            and self.date > today
        ):
            raise ValidationError(
                "Não pode marcar como CONCLUÍDO antes da data do casamento"
            )

    # ── Métodos de Ciclo de Vida da Entidade ─────────────────────────────

    def can_transition_to(self, target_status: str | StatusChoices) -> bool:
        """Verifica se a transição para o status informado é válida."""
        target = str(target_status)
        if self.status == target:
            return True
        allowed = self.ALLOWED_TRANSITIONS.get(self.status, [])
        if target not in allowed:
            return False
        if target == self.StatusChoices.COMPLETED and self.date > timezone.now().date():
            return False
        return True

    def transition_to(self, target_status: str | StatusChoices) -> None:
        """
        Executa a transição de status validando as regras de negócio de domínio.

        Raises:
            BusinessRuleViolation: Se a transição for proibida ou prematura.
        """
        target = str(target_status)
        if self.status == target:
            return

        if not self.can_transition_to(target):
            if (
                target == self.StatusChoices.COMPLETED
                and self.date > timezone.now().date()
            ):
                raise BusinessRuleViolation(
                    detail="Não pode marcar como CONCLUÍDO antes da data do casamento",
                    code="wedding_premature_completion",
                )
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{target}'.",
                code="wedding_invalid_status_transition",
            )

        self.status = self.StatusChoices(target)

    def complete(self) -> None:
        """Conclui o casamento garantindo que o evento já foi realizado."""
        self.transition_to(self.StatusChoices.COMPLETED)

    def cancel(self, reason: str | None = None) -> None:
        """Cancela o casamento."""
        self.transition_to(self.StatusChoices.CANCELED)

    def reopen(self) -> None:
        """Reabre um casamento previamente cancelado voltando para EM ANDAMENTO."""
        self.transition_to(self.StatusChoices.IN_PROGRESS)

    # ── Propriedades de Domínio ──────────────────────────────────────────

    @property
    def is_completed(self) -> bool:
        """Indica se o casamento já foi realizado e concluído."""
        return self.status == self.StatusChoices.COMPLETED

    @property
    def is_canceled(self) -> bool:
        """Indica se o casamento foi cancelado."""
        return self.status == self.StatusChoices.CANCELED

    @property
    def is_in_progress(self) -> bool:
        """Indica se o casamento está com planejamento ativo."""
        return self.status == self.StatusChoices.IN_PROGRESS

    @property
    def is_past(self) -> bool:
        """Indica se a data prevista do evento já ficou no passado."""
        return bool(self.date and self.date < timezone.now().date())

    @property
    def days_until(self) -> int:
        """Retorna os dias restantes até o casamento, ou zero se já passou."""
        if not self.date:
            return 0
        today = timezone.now().date()
        if self.date <= today:
            return 0
        return (self.date - today).days
