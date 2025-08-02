from django.db import models

from apps.items.models import Item
from apps.weddings.models import Wedding


class Contract(models.Model):
    signature_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    item = models.ForeignKey(
        Item, on_delete=models.CASCADE, null=True, blank=True
    )
    wedding = models.ForeignKey(
        Wedding, on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        return f"Contract for {self.item.name} - {self.wedding}"
