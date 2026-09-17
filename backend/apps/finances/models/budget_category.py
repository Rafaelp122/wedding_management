"""
Modelo de Categorias Orçamentárias do domínio financeiro.

Responsabilidade: Gestão de categorias de gastos para agrupamento logístico e
financeiro.

Referência: RF03
"""

from decimal import Decimal
from typing import ClassVar, cast

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum

from apps.core.mixins import WeddingOwnedMixin
from apps.finances.managers import BudgetCategoryManager
from apps.tenants.models import TenantModel


class BudgetCategory(TenantModel, WeddingOwnedMixin):
    """
    Categorias de gastos (RF03).
    Permite o agrupamento logístico e financeiro vinculando despesas a um orçamento.
    """

    objects = BudgetCategoryManager()  # type: ignore[misc]

    DEFAULT_NAMES: ClassVar[list[str]] = [
        "Espaço e Buffet",
        "Decoração e Flores",
        "Fotografia e Vídeo",
        "Música e Iluminação",
        "Assessoria",
        "Trajes e Beleza",
    ]

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
           Esta property dispara uma query ``aggregate`` a cada acesso se não houver
           o atributo anotado ``_total_spent``.
           Para múltiplas categorias, prefira
           ``BudgetCategory.objects.with_total_spent()`` que faz uma única
           query com ``annotate``.
        """
        val = getattr(self, "_total_spent", None)
        if val is not None:
            return cast(Decimal, val)

        from django.db.models import Sum

        from apps.finances.models.installment import Installment

        return self.expenses.aggregate(
            total=Sum(
                "installments__amount",
                filter=Q(installments__status=Installment.StatusChoices.PAID),
            )
        )["total"] or Decimal("0.00")

    def clean(self) -> None:
        """Validações de integridade e conservação do teto orçamentário (BR-F04)."""
        super().clean()
        if (
            self.budget_id
            and self.allocated_budget is not None
            and getattr(self.budget, "total_estimated", None) is not None
        ):
            siblings_qs = self.budget.categories.all()
            if self.pk:
                siblings_qs = siblings_qs.exclude(pk=self.pk)
            allocated_siblings = siblings_qs.aggregate(total=Sum("allocated_budget"))[
                "total"
            ] or Decimal("0.00")
            if allocated_siblings + self.allocated_budget > self.budget.total_estimated:
                raise ValidationError(
                    f"A soma das categorias alocadas "
                    f"({allocated_siblings + self.allocated_budget}) "
                    f"excede o teto do orçamento ({self.budget.total_estimated})."
                )

    # ── Propriedades de Conveniência ─────────────────────────────────────

    @property
    def budget_utilization_percent(self) -> int:
        """Percentual do orçamento alocado consumido (0 a 100+)."""
        if not self.allocated_budget or self.allocated_budget <= Decimal("0.00"):
            return 0
        return int((self.total_spent / self.allocated_budget) * 100)
