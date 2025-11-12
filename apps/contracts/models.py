from django.db import models

from apps.core.models import BaseModel
from apps.items.models import Item
from apps.supplier.models import Supplier
from apps.weddings.models import Wedding


class Contract(BaseModel):
    # Modelo que representa um contrato entre fornecedor, item e casamento
    signature_date = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=50, blank=True)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    wedding = models.ForeignKey(
        Wedding,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    # Retorna uma representação legível do contrato,
    # mostrando o nome do item e o casamento relacionado
    def __str__(self):
        return f"Contract for {self.item.name} - {self.wedding}"
