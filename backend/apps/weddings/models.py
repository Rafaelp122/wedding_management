from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.tenants.models import TenantModel


def validate_future_date(value: date) -> None:
    if value < timezone.now().date():
        raise ValidationError("A data do casamento não pode ser no passado.")


class Wedding(TenantModel):
    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField(validators=[validate_future_date])
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

    def clean(self) -> None:
        """Validações de negócio."""
        super().clean()

        if self.status == self.StatusChoices.COMPLETED:
            if self.date > timezone.now().date():
                raise ValidationError(
                    "Não pode marcar como CONCLUÍDO antes da data do casamento"
                )
