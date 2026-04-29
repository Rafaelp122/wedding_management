from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.tenants.mixins import CompanyOwnedMixin


class Appointment(BaseModel, CompanyOwnedMixin):
    """
    Representa um compromisso na agenda do organizador (RF07).
    Um compromisso pode ou não estar vinculado a um casamento específico.
    """

    class EventType(models.TextChoices):
        MEETING = "MEETING", "Reunião"
        VISIT = "VISIT", "Visita Técnica"
        DEGUSTATION = "DEGUSTATION", "Degustação"
        CEREMONY = "CEREMONY", "Cerimônia"
        OTHER = "OTHER", "Outro"

    event = models.ForeignKey(
        "events.Event",
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.MEETING,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Compromisso"
        verbose_name_plural = "Compromissos"
        ordering = ["start_time"]
        indexes = [
            models.Index(fields=["company", "start_time"]),
            models.Index(fields=["event", "start_time"]),
            models.Index(fields=["event_type"]),
            models.Index(fields=["start_time"]),
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_event_type_display()})"

    def clean(self) -> None:
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "A hora de início deve ser anterior à hora de término."
                )

        if self.start_time and self.start_time < timezone.now():
            # Nota: Em alguns casos reais pode-se permitir retroativo,
            # mas para o MVP/RF07 vamos manter estrito.
            pass
