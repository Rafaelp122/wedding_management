from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.tenants.mixins import CompanyOwnedMixin


def validate_future_date(value: date) -> None:
    if value < timezone.now().date():
        raise ValidationError("A data do evento não pode ser no passado.")


class Event(BaseModel, CompanyOwnedMixin):
    """
    Entidade principal de um Evento B2B (ADR-016).
    Um evento pertence a uma Company e pode ter detalhes específicos
    (ex: WeddingDetail).
    """

    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    class EventType(models.TextChoices):
        WEDDING = "WEDDING", "Casamento"
        CORPORATE = "CORPORATE", "Corporativo"
        SOCIAL = "SOCIAL", "Social (Aniversário, etc)"
        OTHER = "OTHER", "Outro"

    name = models.CharField("Nome do Evento", max_length=255)
    event_type = models.CharField(
        max_length=20,
        choices=EventType.choices,
        default=EventType.WEDDING,
    )
    date = models.DateField(validators=[validate_future_date])
    location = models.CharField(max_length=255)
    expected_guests = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Número de Convidados",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["company", "status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["event_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.date})"

    def clean(self) -> None:
        """Regras de negócio do domínio de eventos."""
        super().clean()

        # BR-E01: Não pode marcar como CONCLUÍDO um evento em data futura.
        if (
            self.status == self.StatusChoices.COMPLETED
            and self.date > timezone.now().date()
        ):
            raise ValidationError(
                {"status": "Não é possível concluir um evento agendado para o futuro."}
            )


class WeddingDetail(models.Model):
    """
    Detalhes específicos para eventos do tipo Casamento (ADR-016).
    Relacionamento 1:1 com Event.
    """

    event = models.OneToOneField(
        Event,
        on_delete=models.CASCADE,
        related_name="wedding_detail",
        primary_key=True,
    )
    groom_name = models.CharField("Nome do Noivo", max_length=100)
    bride_name = models.CharField("Nome da Noiva", max_length=100)

    class Meta:
        verbose_name = "Detalhe de Casamento"
        verbose_name_plural = "Detalhes de Casamentos"

    def __str__(self) -> str:
        return f"Detalhes: {self.bride_name} & {self.groom_name}"
