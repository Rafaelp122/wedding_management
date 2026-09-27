from datetime import datetime
from typing import Any

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.scheduler.managers import EventQuerySet
from apps.tenants.models import TenantModel


class Event(TenantModel, WeddingOwnedMixin):
    """Modelo que representa um evento/compromisso no calendário."""

    objects = EventQuerySet.as_manager()  # type: ignore[assignment,misc]

    class TypeChoices(models.TextChoices):
        """Tipos de eventos disponíveis no calendário."""

        MEETING = "reuniao", "Reunião"
        PAYMENT = "pagamento", "Pagamento"
        VISIT = "visita", "Visita Técnica"
        TASTING = "degustacao", "Degustação"
        OTHER = "outro", "Outro"

    class RecurrenceChoices(models.TextChoices):
        """Regras de recorrência para eventos do calendário."""

        NONE = "none", "Não recorrente"
        WEEKLY = "semanal", "Semanal"
        BIWEEKLY = "quinzenal", "Quinzenal"
        MONTHLY = "mensal", "Mensal"

    title = models.CharField(max_length=255, verbose_name="Título")
    location = models.CharField(max_length=255, blank=True, verbose_name="Local")
    description = models.TextField(blank=True, verbose_name="Descrição")
    event_type = models.CharField(
        max_length=50,
        choices=TypeChoices.choices,
        default=TypeChoices.OTHER,
        verbose_name="Tipo de Evento",
    )

    start_time = models.DateTimeField(verbose_name="Início do Evento")
    end_time = models.DateTimeField(verbose_name="Fim do Evento", null=True, blank=True)

    recurrence_rule = models.CharField(
        max_length=20,
        choices=RecurrenceChoices.choices,
        default=RecurrenceChoices.NONE,
        verbose_name="Regra de Recorrência",
        help_text="Frequência com que o evento se repete",
    )

    reminder_enabled = models.BooleanField(
        default=False,
        verbose_name="Lembrete Ativo",
        help_text="Enviar lembrete automático",
    )
    reminder_minutes_before = models.PositiveIntegerField(
        default=60,
        verbose_name="Lembrete (minutos antes)",
        help_text="Quantos minutos antes do evento enviar lembrete",
    )

    source_installment = models.ForeignKey(
        "finances.Installment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Parcela de origem",
        help_text="Parcela financeira que gerou este evento (apenas PAYMENT)",
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["company", "start_time"]),
            models.Index(fields=["wedding", "start_time"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["start_time"]),
        ]

    def __str__(self) -> str:
        return self.title

    def clean(self) -> None:
        """Valida integridade do intervalo de horários e proteção de pagamento."""
        super().clean()
        if self.end_time and self.start_time and self.end_time < self.start_time:
            raise ValidationError(
                {
                    "end_time": (
                        "A hora de término não pode ser anterior à hora de início."
                    )
                }
            )

        # BR-S01: Blindagem de eventos de pagamento contra mutação indevida
        if self.pk and not getattr(self, "_allow_payment_mutation", False):
            orig = (
                Event.objects.filter(pk=self.pk)
                .values("event_type", "start_time", "end_time", "title")
                .first()
            )
            if orig:
                if orig["event_type"] == self.TypeChoices.PAYMENT:
                    if (
                        self.event_type != self.TypeChoices.PAYMENT
                        or self.start_time != orig["start_time"]
                        or self.end_time != orig["end_time"]
                        or self.title != orig["title"]
                    ):
                        raise ValidationError(
                            "Eventos de pagamento são gerados automaticamente "
                            "e não podem ser editados manualmente."
                        )
                elif (
                    orig["event_type"] != self.TypeChoices.PAYMENT
                    and self.event_type == self.TypeChoices.PAYMENT
                ):
                    raise ValidationError(
                        "Não é permitido alterar o tipo de um evento para 'pagamento'."
                    )

    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Deleção blindada conforme BR-S01 (eventos de pagamento são protegidos)."""
        skip_payment_guard = kwargs.pop("skip_payment_guard", False)
        if (
            self.is_payment_event
            and not skip_payment_guard
            and not getattr(self, "_allow_payment_mutation", False)
        ):
            raise BusinessRuleViolation(
                detail=(
                    "Eventos de pagamento são gerados automaticamente e não podem ser "
                    "deletados manualmente. Acesse o módulo financeiro para ajustar."
                ),
                code="payment_event_readonly",
            )
        return super().delete(*args, **kwargs)

    # ── Propriedades Semânticas ──────────────────────────────────────────

    @property
    def is_payment_event(self) -> bool:
        """Indica se o evento é do tipo pagamento."""
        return self.event_type == self.TypeChoices.PAYMENT

    # ── Métodos de Domínio ───────────────────────────────────────────────

    def reschedule(
        self, start_time: datetime, end_time: datetime | None = None
    ) -> None:
        """Reagenda o evento para novo horário validando suas invariantes.

        Args:
            start_time: Novo início do evento.
            end_time: Novo término do evento opcional.
        """
        self.start_time = start_time
        self.end_time = end_time
        self.clean()

    def enable_reminder(self, minutes_before: int = 60) -> None:
        """Habilita o lembrete automático com antecedência em minutos.

        Args:
            minutes_before: Antecedência em minutos para disparo do lembrete.
        """
        self.reminder_enabled = True
        self.reminder_minutes_before = minutes_before

    def disable_reminder(self) -> None:
        """Desabilita o lembrete automático do evento."""
        self.reminder_enabled = False
