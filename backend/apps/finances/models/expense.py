"""
Modelo de Despesas do domínio financeiro.

Responsabilidade: Gestão de despesas vinculadas a categorias orçamentárias e contratos.

Referências: RF04, RF05
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.tenants.models import TenantModel


class Expense(TenantModel, WeddingOwnedMixin):
    """
    Compromisso financeiro real (RF03/RF04).
    Liga o financeiro à logística (Contract).
    """

    category = models.ForeignKey(
        "finances.BudgetCategory", on_delete=models.PROTECT, related_name="expenses"
    )
    contract = models.OneToOneField(
        "logistics.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense",
    )
    description = models.CharField(max_length=255)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        app_label = "finances"
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["category"]),
        ]

    def clean(self) -> None:
        super().clean()

        # TOLERÂNCIA ZERO: A soma das parcelas deve ser EXATA
        if self.pk and self.actual_amount:
            total_installments = self.installments.aggregate(models.Sum("amount"))[
                "amount__sum"
            ] or Decimal("0.00")
            if total_installments != self.actual_amount:
                raise ValidationError(
                    f"ERRO DE INTEGRIDADE: A soma das parcelas (R${total_installments}) "  # noqa
                    f"não bate com o valor total (R${self.actual_amount})."
                )
