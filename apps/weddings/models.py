from django.db import models

from apps.client.models import Client
from apps.users.models import User


class Wedding(models.Model):
    planner = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.OneToOneField(
        Client,
        on_delete=models.SET_NULL,
        related_name="weddings",
        blank=True,
        null=True,
    )
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"
