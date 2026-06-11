"""
QuerySet e Manager customizados para o domínio financeiro.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Q, Sum
from django.db.models.functions import Coalesce

from apps.finances.models.installment import Installment
from apps.tenants.managers import TenantManager, TenantQuerySet


class BudgetCategoryQuerySet(TenantQuerySet):
    """QuerySet customizado para BudgetCategory."""

    def with_total_spent(self) -> BudgetCategoryQuerySet:
        """Anota cada categoria com o total pago (soma de parcelas PAID)."""
        return self.annotate(
            _total_spent=Coalesce(
                Sum(
                    "expenses__installments__amount",
                    filter=Q(
                        expenses__installments__status=Installment.StatusChoices.PAID
                    ),
                ),
                Decimal("0.00"),
            )
        )


class BudgetCategoryManager(TenantManager):
    """Manager customizado para BudgetCategory."""

    def get_queryset(self) -> BudgetCategoryQuerySet:
        return BudgetCategoryQuerySet(self.model, using=self._db)
