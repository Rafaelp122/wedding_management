import uuid
from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel
from apps.items.models import Item


class Contract(BaseModel):
    """
    Modelo de Contrato Tripartite.
    """
    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="contract")
    description = models.TextField(blank=True, help_text="Cláusulas específicas ou descrição do serviço.")
    
    STATUS_CHOICES = (
        ("DRAFT", "Rascunho"),
        ("WAITING_PLANNER", "Aguardando Cerimonialista"),
        ("WAITING_SUPPLIER", "Aguardando Fornecedor"),
        ("WAITING_COUPLE", "Aguardando Noivos"),
        ("COMPLETED", "Concluído"),
        ("CANCELED", "Cancelado"),
    )
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="WAITING_PLANNER")

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    # Assinaturas
    planner_signature = models.FileField(upload_to="signatures/planner/", null=True, blank=True)
    planner_signed_at = models.DateTimeField(null=True, blank=True)
    planner_ip = models.GenericIPAddressField(null=True, blank=True)

    supplier_signature = models.FileField(upload_to="signatures/supplier/", null=True, blank=True)
    supplier_signed_at = models.DateTimeField(null=True, blank=True)
    supplier_ip = models.GenericIPAddressField(null=True, blank=True)

    couple_signature = models.FileField(upload_to="signatures/couple/", null=True, blank=True)
    couple_signed_at = models.DateTimeField(null=True, blank=True)
    couple_ip = models.GenericIPAddressField(null=True, blank=True)

    integrity_hash = models.CharField(max_length=64, blank=True, null=True)
    final_pdf = models.FileField(upload_to="contracts_pdf/", null=True, blank=True)

    def __str__(self):
        return f"Contrato {self.status} - {self.item.name}"

    @property
    def supplier(self):
        # Retorna o nome do fornecedor (string) do item
        return self.item.supplier

    @property
    def wedding(self):
        return self.item.wedding

    @property
    def contract_value(self):
        """
        Retorna o custo total do item usando a propriedade do modelo Item.
        """
        if not self.item:
            return 0
        # Usa a propriedade total_cost definida no Item (unit_price * quantity)
        return self.item.total_cost

    def get_absolute_url(self):
        return reverse("contracts:sign_contract", kwargs={"token": self.token})

    def save(self, *args, **kwargs):
        if not self.status:
            self.status = "WAITING_PLANNER"
        super().save(*args, **kwargs)