from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from apps.core.models import BaseModel
from apps.users.models import User


class Wedding(BaseModel):
    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    planner = models.ForeignKey(User, on_delete=models.CASCADE)
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

    class Meta:
        verbose_name = "Casamento"
        verbose_name_plural = "Casamentos"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["planner", "status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"

    def clean(self):
        """Validações de negócio."""
        super().clean()

        if self.status == self.StatusChoices.COMPLETED:
            if self.date > timezone.now().date():
                raise ValidationError(
                    "Não pode marcar como CONCLUÍDO antes da data do casamento"
                )
