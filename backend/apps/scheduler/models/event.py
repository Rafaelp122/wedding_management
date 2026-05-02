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
