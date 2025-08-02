from django.db import models

from apps.supplier.models import Supplier
from apps.weddings.models import Wedding


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)
    wedding = models.ForeignKey(Wedding, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
