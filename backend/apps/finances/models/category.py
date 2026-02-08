"""
Modelo de Categorias Orçamentárias do domínio financeiro.

Responsabilidade: Gestão de categorias de gastos para agrupamento logístico e
financeiro.

Referência: RF03
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import SoftDeleteModel, WeddingOwnedModel


class BudgetCategory(SoftDeleteModel, WeddingOwnedModel):
    """
    Categorias de gastos (RF03).
    Permite o agrupamento logístico e financeiro.
    """

    budget = models.ForeignKey(
        "finances.Budget",
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Orçamento Pai",
    )
    name = models.CharField(max_length=100, verbose_name="Nome da Categoria")
    description = models.TextField(blank=True, verbose_name="Descrição")
    allocated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Verba Alocada",
    )

    class Meta:
        app_label = "finances"
        verbose_name = "Categoria de Orçamento"
        verbose_name_plural = "Categorias de Orçamento"
        unique_together = [["budget", "name"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.wedding})"

    def clean(self):
        super().clean()
        # TRAVA DE SEGURANÇA: Garante que o orçamento e a categoria são do
        # mesmo casamento
        if self.budget.wedding != self.wedding:
            raise ValidationError(
                "O orçamento pai deve pertencer ao mesmo casamento desta categoria."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
