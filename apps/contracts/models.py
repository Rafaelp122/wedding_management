from django.db import models

from apps.budget.models import Budget
from apps.client.models import Client
from apps.users.models import Planner


class Contract(models.Model):
    signature_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)

    def __str__(self):
        return f'Contract #{self.id}'