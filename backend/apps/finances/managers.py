"""
QuerySet e Manager customizados para o domínio financeiro.
"""

from __future__ import annotations

from decimal import Decimal

from django.db.models import Count, Q, Sum
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


class ExpenseQuerySet(TenantQuerySet):
    """QuerySet customizado para Expense."""

    def with_details(self) -> ExpenseQuerySet:
        """Anota cada despesa com contagem de parcelas e valores totais."""
        return self.select_related("category", "contract", "wedding").annotate(
            installments_count=Count("installments"),
            paid_installments_count=Count(
                "installments",
                filter=Q(installments__status=Installment.StatusChoices.PAID),
            ),
            total_paid=Coalesce(
                Sum(
                    "installments__amount",
                    filter=Q(installments__status=Installment.StatusChoices.PAID),
                ),
                Decimal("0.00"),
            ),
            total_pending=Coalesce(
                Sum(
                    "installments__amount",
                    filter=Q(
                        installments__status__in=[
                            Installment.StatusChoices.PENDING,
                            Installment.StatusChoices.OVERDUE,
                        ]
                    ),
                ),
                Decimal("0.00"),
            ),
        )


class ExpenseManager(TenantManager):
    """Manager customizado para Expense."""

    def get_queryset(self) -> ExpenseQuerySet:
        return ExpenseQuerySet(self.model, using=self._db)
