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

from apps.core.mixins import WeddingOwnedMixin
from apps.finances.managers import BudgetCategoryManager
from apps.tenants.models import TenantModel


class BudgetCategory(TenantModel, WeddingOwnedMixin):
    """
    Categorias de gastos (RF03).
    Permite o agrupamento logístico e financeiro vinculando despesas a um orçamento.
    """

    objects = BudgetCategoryManager()  # type: ignore[misc]

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
        ordering = ["name"]
        indexes = [
            models.Index(fields=["company", "budget"]),
            models.Index(fields=["name"]),
        ]
        unique_together = [["budget", "name"]]

    def __str__(self) -> str:
        return f"{self.name} ({self.wedding})"

    @property
    def total_spent(self) -> Decimal:
        """
        Retorna o total efetivamente pago nesta categoria, somando apenas
        o ``amount`` das parcelas com status ``PAID``.

        .. warning::
           Esta property dispara uma query ``aggregate`` a cada acesso.
           Para múltiplas categorias, prefira
           ``BudgetCategory.objects.with_total_spent()`` que faz uma única
           query com ``annotate``.
        """
        from django.db.models import Q, Sum

        from apps.finances.models.installment import Installment

        return self.expenses.aggregate(
            total=Sum(
                "installments__amount",
                filter=Q(installments__status=Installment.StatusChoices.PAID),
            )
        )["total"] or Decimal("0.00")

    def clean(self) -> None:
        super().clean()

        # TRAVA DE SEGURANÇA: Garante que o orçamento e a categoria são do mesmo casamento # noqa
        if self.budget.wedding != self.wedding:
            raise ValidationError(
                "O orçamento pai deve pertencer ao mesmo casamento desta categoria."
            )
