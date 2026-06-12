from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.tenants.models import TenantModel


class Event(TenantModel, WeddingOwnedMixin):
    """Modelo que representa um evento/compromisso no calendário."""

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
