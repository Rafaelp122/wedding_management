from django.db import models

from apps.client.models import Client
from apps.users.models import User


class Wedding(models.Model):
    planner = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.OneToOneField(
        Client, on_delete=models.CASCADE, related_name="weddings"
    )
    groom_name = models.CharField(max_length=100, blank=True, null=True)
    bride_name = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        if self.groom_name and self.bride_name:
            return f"{self.groom_name} & {self.bride_name} - {self.date}"
        elif self.client:
            return f"{self.client.name} - {self.date}"
        else:
            return f"Wedding on {self.date}"
