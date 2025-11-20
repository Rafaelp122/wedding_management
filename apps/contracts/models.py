from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.items.models import Item


class Contract(BaseModel):
    """
    Representa o contrato financeiro/jurídico associado a um item do casamento.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pendente"),
        ("SIGNED", "Assinado"),
        ("COMPLETED", "Finalizado"),
        ("CANCELED", "Cancelado"),
    ]

    item = models.OneToOneField(
        Item, 
        on_delete=models.CASCADE, 
        related_name="contract",
        verbose_name="Item"
    )
    signature_date = models.DateField("Data de Assinatura", null=True, blank=True)
    expiration_date = models.DateField("Data de Vencimento", null=True, blank=True)
    description = models.TextField("Descrição/Observações", blank=True)

    status = models.CharField(
        "Status",
        max_length=20, 
        choices=STATUS_CHOICES, 
        default="PENDING"
    )

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"

    def __str__(self):
        return f"Contrato: {self.item.name}"

    @property
    def supplier(self):
        # Acessa o fornecedor diretamente do item relacionado
        return self.item.supplier

    @property
    def wedding(self):
        # Acessa o casamento diretamente do item relacionado
        return self.item.wedding

    def clean(self):
        """Validações customizadas do modelo."""
        # Garante que a data de expiração não seja anterior à assinatura
        if self.signature_date and self.expiration_date:
            if self.expiration_date < self.signature_date:
                raise ValidationError({
                    "expiration_date": "A data de vencimento não pode ser anterior à data de assinatura."
                })
