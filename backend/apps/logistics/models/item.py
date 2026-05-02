"""
Modelo de Itens do domínio logístico.

Responsabilidade: Gestão de itens de logística, representando necessidades físicas e
serviços contratados.

Referências: RF07-RF08
"""

from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.tenants.models import TenantModel

from .contract import Contract
from .supplier import Supplier


class Item(TenantModel, WeddingOwnedMixin):
    """
    Item de logística (RF07-RF08).
    Representa a necessidade física ou o serviço contratado.
    """

    class AcquisitionStatus(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        DONE = "DONE", "Concluído"

    # Relação N:1 - Muitos itens podem pertencer ao mesmo contrato
    contract = models.ForeignKey(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Contrato",
        help_text="Contrato associado a este item",
    )

    name = models.CharField(max_length=255, verbose_name="Nome do Item")
    description = models.TextField(blank=True, verbose_name="Descrição/Especificações")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantidade")

    acquisition_status = models.CharField(
        max_length=20,
        choices=AcquisitionStatus.choices,
        default=AcquisitionStatus.PENDING,
        verbose_name="Status de Entrega/Logística",
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["acquisition_status"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.quantity}x)"

    @property
    def supplier(self) -> Supplier | None:
        """Fornecedor vem do contrato associado."""
        return self.contract.supplier if self.contract else None
