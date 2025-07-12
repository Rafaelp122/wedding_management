from django.db import models

from apps.contracts.models import Contract
from apps.users.models import Planner


class Schedule(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    datetime = models.DateTimeField()
    type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
