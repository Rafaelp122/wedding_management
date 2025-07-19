from django.db import models

from apps.client.models import Client
from apps.users.models import Planner

class Wedding(models.Model):
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client, blank=True)
    groom_name = models.CharField(max_length=100, blank=True, null=True)
    bride_name = models.CharField(max_length=100, blank=True, null=True)
    contract = models.OneToOneField(
        "contracts.Contract", on_delete=models.SET_NULL, null=True, blank=True
    )
    date = models.DateField()
    location = models.CharField(max_length=255)

    def __str__(self):
        if self.groom_name and self.bride_name:
            return f"{self.groom_name} & {self.bride_name} - {self.date}"
        names = " & ".join([c.name.split()[0] for c in self.clients.all()])
        return f"{names} - {self.date}"
