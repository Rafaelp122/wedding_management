from django.db import models

from apps.core.models import BaseModel  # fornece created_at e updated_at
from apps.users.models import User

from .querysets import WeddingQuerySet


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
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )

    objects = WeddingQuerySet.as_manager()

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"
