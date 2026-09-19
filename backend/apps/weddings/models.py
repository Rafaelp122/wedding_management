from __future__ import annotations

import datetime as dt
from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation
from apps.tenants.models import TenantModel
from apps.weddings.managers import WeddingQuerySet


def validate_future_date(value: date) -> None:
    """Validador auxiliar mantido para compatibilidade com migration 0001."""
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
            self.status == self.StatusChoices.IN_PROGRESS
            and self.date
            and self.date < today
        ):
            if self._state.adding:
                raise ValidationError(
                    {"date": "A data do casamento não pode ser no passado."}
                )
            elif self.pk:
                orig = Wedding.objects.filter(pk=self.pk).values("date").first()
                if orig and orig["date"] != self.date:
                    raise ValidationError(
                        {"date": "A nova data do casamento não pode ser no passado."}
                    )

        if (
            self.status == self.StatusChoices.COMPLETED
            and self.date
            and self.date > today
        ):
            raise ValidationError(
                "Não pode marcar como CONCLUÍDO antes da data do casamento"
            )

        if self.pk:
            orig_status = Wedding.objects.filter(pk=self.pk).values("status").first()
            if orig_status and orig_status["status"] != self.status:
                allowed = self.ALLOWED_TRANSITIONS.get(orig_status["status"], [])
                if self.status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de "
                        f"'{orig_status['status']}' para '{self.status}'."
                    )

    # ── Métodos de Ciclo de Vida e Operações de Domínio ─────────────────

    def reschedule(self, new_date: dt.date) -> None:
        """
        Reagenda a data do casamento validando as regras temporais.

        Args:
            new_date: Nova data pretendida para a realização da cerimônia.

        Raises:
            BusinessRuleViolation: Se o casamento já estiver concluído ou a data
                for no passado.
        """
        if self.is_completed:
            raise BusinessRuleViolation(
                detail="Não é possível reagendar um casamento já concluído.",
                code="wedding_already_completed",
            )
        if new_date < timezone.now().date():
            raise BusinessRuleViolation(
                detail="A nova data do casamento não pode ser no passado.",
                code="wedding_reschedule_in_past",
            )
        self.date = new_date

    def update_details(
        self,
        *,
        groom_name: str | None = None,
        bride_name: str | None = None,
        location: str | None = None,
        expected_guests: int | object | None = ...,
    ) -> None:
        """
        Atualiza dados cadastrais descritivos do casamento.

        Args:
            groom_name: Nome do noivo.
            bride_name: Nome da noiva.
            location: Local planejado para a realização.
            expected_guests: Quantidade estimada de convidados.
        """
        if groom_name is not None:
            self.groom_name = groom_name
        if bride_name is not None:
            self.bride_name = bride_name
        if location is not None:
            self.location = location
        if expected_guests is not ...:
            self.expected_guests = expected_guests  # type: ignore[assignment]

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

    def cancel(self) -> None:
        """Cancela o casamento."""
        self.transition_to(self.StatusChoices.CANCELED)

    def reopen(self) -> None:
        """Reabre um casamento previamente cancelado voltando para EM ANDAMENTO."""
        self.transition_to(self.StatusChoices.IN_PROGRESS)

    # ── Propriedades e Métodos de Domínio ────────────────────────────────

    @property
    def display_name(self) -> str:
        """Retorna o nome formatado de exibição canônica do casamento."""
        return f"Casamento de {self.bride_name} e {self.groom_name}"

    @property
    def is_completed(self) -> bool:
        """Indica se o casamento já foi realizado e concluído."""
        return self.status == self.StatusChoices.COMPLETED

    def get_days_until(self, reference_date: dt.date | None = None) -> int:
        """Retorna dias restantes até o casamento com suporte a data de referência."""
        if not self.date:
            return 0
        ref = reference_date or timezone.now().date()
        if self.date <= ref:
            return 0
        return (self.date - ref).days
