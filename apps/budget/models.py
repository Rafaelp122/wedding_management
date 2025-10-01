from django.db import models
from apps.users.models import Planner
from apps.weddings.models import Wedding 


class Budget(models.Model):
    initial_estimate = models.DecimalField(max_digits=10, decimal_places=2)
    final_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    planner = models.ForeignKey(Planner, on_delete=models.CASCADE)
    wedding = models.OneToOneField(
        Wedding, on_delete=models.CASCADE, related_name="budget", null=False
    )

    def __str__(self):
        return f"Budget #{self.pk}"
