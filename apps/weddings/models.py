from django.db import models

from apps.users.models import User

from .querysets import WeddingQuerySet


class Wedding(models.Model):
    planner = models.ForeignKey(User, on_delete=models.CASCADE)
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    STATUS_CHOICES = [
        ('IN_PROGRESS', 'Em Andamento'),
        ('COMPLETED', 'Concluído'),
        ('CANCELED', 'Cancelado'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='IN_PROGRESS'
    )

    objects = WeddingQuerySet.as_manager()

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"
