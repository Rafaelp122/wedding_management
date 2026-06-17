"""
Modelo de Itens do domínio logístico.

Responsabilidade: Gestão de itens de logística, representando necessidades físicas e
serviços contratados.

Referências: RF07-RF08
"""

from collections.abc import Collection
from typing import Any, ClassVar, Self

from django.core.exceptions import ValidationError
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

    _original_acquisition_status: str | None = None

    ALLOWED_TRANSITIONS: ClassVar[dict[str, list[str]]] = {
        "PENDING": ["IN_PROGRESS"],
        "IN_PROGRESS": ["DONE", "PENDING"],
        "DONE": ["IN_PROGRESS"],
    }

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

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._original_acquisition_status = self.acquisition_status

    def __str__(self) -> str:
        return f"{self.name} ({self.quantity}x)"

    @classmethod
    def from_db(
        cls, db: str | None, field_names: Collection[str], values: Collection[Any]
    ) -> Self:
        instance = super().from_db(db, field_names, values)
        instance._original_acquisition_status = instance.acquisition_status
        return instance

    def clean(self) -> None:
        super().clean()

        if not self._state.adding:
            original = self._original_acquisition_status
            if original is None:
                msg = (
                    "Não foi possível determinar o status original do item. "
                    "Recarregue a instância do banco e tente novamente."
                )
                raise ValidationError(msg)
            if self.acquisition_status != original:
                allowed = self.ALLOWED_TRANSITIONS.get(original, [])
                if self.acquisition_status not in allowed:
                    raise ValidationError(
                        f"Não é permitido transitar de '{original}' para "
                        f"'{self.acquisition_status}'."
                    )

    @property
    def supplier(self) -> Supplier | None:
        """Fornecedor vem do contrato associado."""
        return self.contract.supplier if self.contract else None
