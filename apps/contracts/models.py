from django.db import models

from apps.core.models import BaseModel
from apps.items.models import Item


class Contract(BaseModel):
    # Modelo que representa um contrato vinculado a um item de casamento
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="contract")
    signature_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, default="PENDING")

    # Retorna uma representação legível do contrato
    def __str__(self):
        return f"Contrato para {self.item.name}"

    @property
    def supplier(self):
        # Acessa o fornecedor diretamente do item relacionado
        return self.item.supplier

    @property
    def wedding(self):
        # Acessa o casamento diretamente do item relacionado
        return self.item.wedding
