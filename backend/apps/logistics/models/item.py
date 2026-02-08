"""
Modelo de Itens do domínio logístico.

Responsabilidade: Gestão de itens de logística, representando necessidades físicas e
serviços contratados.

Referências: RF07-RF08
"""

from django.db import models

from apps.core.models import SoftDeleteModel, WeddingOwnedModel

from .contract import Contract


class Item(SoftDeleteModel, WeddingOwnedModel):
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

    # Ligação necessária para o Dashboard Financeiro saber onde este item 'mora'
    budget_category = models.ForeignKey(
        "finances.BudgetCategory",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Categoria Orçamental",
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.quantity}x)"

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError

        # RF07.1: A trava contra cross-contamination de orçamentos
        if self.budget_category.wedding != self.wedding:
            raise ValidationError(
                "A categoria de orçamento selecionada não pertence a este casamento."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def supplier(self):
        """Fornecedor vem do contrato associado."""
        return self.contract.supplier if self.contract else None
