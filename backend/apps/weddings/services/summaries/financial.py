import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Q, Sum

from apps.finances.models import Budget, BudgetCategory, Installment
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class FinancialSummaryService:
    @staticmethod
    def pending_installments_7d(
        *, company: Company, today: date | None = None
    ) -> Decimal:
        """Return total amount of pending installments due within the next 7 days."""
        today = today or date.today()
        seven_days = today + timedelta(days=7)
        total = (
            Installment.objects.for_tenant(company)
            .filter(
                status=Installment.StatusChoices.PENDING,
                due_date__gte=today,
                due_date__lte=seven_days,
            )
            .aggregate(total=Sum("amount"))["total"]
        )
        return total or Decimal("0.00")

    @staticmethod
    def overdue_installments(
        *, company: Company, today: date | None = None
    ) -> tuple[Decimal, int]:
        """Return total amount and count of overdue installments."""
        today = today or date.today()
        qs = Installment.objects.for_tenant(company).filter(
            Q(status=Installment.StatusChoices.OVERDUE)
            | Q(status=Installment.StatusChoices.PENDING, due_date__lt=today)
        )
        amount = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        return amount, qs.count()

    @staticmethod
    def budget_percentage_used(*, company: Company, wedding: Wedding) -> float:
        """Return the percentage of total estimated budget spent, capped at 100%."""
        try:
            budget = Budget.objects.for_tenant(company).get(wedding=wedding)
            total_spent = budget.total_overall_spent
            total_est = budget.total_estimated
            if total_est > 0:
                pct = float(total_spent) / float(total_est) * 100
                return min(100.0, round(pct, 1))
            return 0.0
        except Budget.DoesNotExist:
            return 0.0

    @staticmethod
    def upcoming_installments(
        *, company: Company, wedding: Wedding, today: date | None = None
    ) -> list[dict[str, Any]]:
        """Return up to 5 upcoming unpaid installments within 30 days for a wedding."""
        today = today or date.today()
        thirty_days = today + timedelta(days=30)
        installments = (
            Installment.objects.for_tenant(company)
            .filter(wedding=wedding)
            .exclude(status=Installment.StatusChoices.PAID)
            .filter(
                Q(due_date__lte=thirty_days)
                | Q(status=Installment.StatusChoices.OVERDUE)
            )
            .order_by("due_date")[:5]
        )
        return [
            {
                "uuid": inst.uuid,
                "installment_number": inst.installment_number,
                "amount": str(inst.amount),
                "due_date": inst.due_date,
                "status": inst.status,
            }
            for inst in installments
        ]

    @staticmethod
    def categories_summary(
        *, company: Company, wedding: Wedding
    ) -> list[dict[str, Any]]:
        """Return a summary of budget categories with allocated and spent."""
        categories = (
            BudgetCategory.objects.for_tenant(company)
            .filter(wedding=wedding)
            .select_related("budget")
            .with_total_spent()  # type: ignore[attr-defined]
        )
        result = []
        for cat in categories:
            spent = cat._total_spent
            alloc = cat.allocated_budget
            pct = round(float(spent) / float(alloc) * 100) if alloc > 0 else 0
            result.append(
                {
                    "name": cat.name,
                    "allocated": str(alloc),
                    "spent": str(spent),
                    "percentage": min(pct, 100),
                }
            )
        logger.info(
            f"Categorias computadas: wedding={wedding.uuid}, total={len(result)}"
        )
        return result
