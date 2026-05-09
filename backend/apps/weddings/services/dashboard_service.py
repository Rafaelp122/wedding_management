import logging
from datetime import date, timedelta
from uuid import UUID

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce

from apps.finances.models import Budget, BudgetCategory, Installment
from apps.logistics.models import Contract
from apps.scheduler.models import Event, Task
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class DashboardService:
    @staticmethod
    def get_summary(company: Company) -> dict:
        today = date.today()
        seven_days = today + timedelta(days=7)
        ninety_days = today + timedelta(days=90)

        active_weddings = (
            Wedding.objects.for_tenant(company)
            .filter(status=Wedding.StatusChoices.IN_PROGRESS)
            .count()
        )

        pending_7d = (
            (
                Installment.objects.for_tenant(company)
                .filter(
                    status=Installment.StatusChoices.PENDING,
                    due_date__gte=today,
                    due_date__lte=seven_days,
                )
                .aggregate(total=Sum("amount"))["total"]
            )
            or 0
        )

        events_week = (
            Event.objects.for_tenant(company)
            .filter(
                start_time__date__gte=today,
                start_time__date__lte=seven_days,
            )
            .count()
        )

        urgent_tasks_count = (
            Task.objects.for_tenant(company)
            .filter(is_completed=False, due_date__lte=today)
            .count()
        )

        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = today.replace(year=today.year + 1, month=1, day=1)
        else:
            month_end = today.replace(month=today.month + 1, day=1)

        weddings_this_month = (
            Wedding.objects.for_tenant(company)
            .filter(date__gte=month_start, date__lt=month_end)
            .count()
        )

        critical_qs = (
            Wedding.objects.for_tenant(company)
            .filter(
                status=Wedding.StatusChoices.IN_PROGRESS,
                date__lte=ninety_days,
            )
            .annotate(
                incomplete_tasks=Count(
                    "task_records",
                    filter=Q(task_records__is_completed=False),
                    distinct=True,
                ),
                pending_installments=Count(
                    "installment_records",
                    filter=Q(
                        installment_records__status=Installment.StatusChoices.PENDING,
                    ),
                    distinct=True,
                ),
                overdue_tasks=Count(
                    "task_records",
                    filter=Q(
                        task_records__is_completed=False,
                        task_records__due_date__lt=today,
                    ),
                    distinct=True,
                ),
                overdue_installments=Count(
                    "installment_records",
                    filter=Q(
                        installment_records__status=Installment.StatusChoices.OVERDUE,
                    ),
                    distinct=True,
                ),
            )
            .order_by("date")
        )

        critical_weddings = []
        for w in critical_qs[:5]:
            days_until = max(0, (w.date - today).days)
            critical_weddings.append(
                {
                    "uuid": w.uuid,
                    "groom_name": w.groom_name,
                    "bride_name": w.bride_name,
                    "days_until": days_until,
                    "incomplete_tasks": w.incomplete_tasks,
                    "pending_installments": w.pending_installments,
                    "overdue_tasks": w.overdue_tasks,
                    "overdue_installments": w.overdue_installments,
                }
            )

        return {
            "active_weddings": active_weddings,
            "pending_installments_7d": str(pending_7d),
            "events_this_week": events_week,
            "urgent_tasks_count": urgent_tasks_count,
            "weddings_this_month": weddings_this_month,
            "critical_weddings": critical_weddings,
        }

    @staticmethod
    def get_wedding_overview(company: Company, wedding_uuid: UUID) -> dict:
        from apps.weddings.services import WeddingService

        wedding = WeddingService.get(company, wedding_uuid)
        today = date.today()
        days_until = max(0, (wedding.date - today).days)

        # Budget
        try:
            budget = Budget.objects.for_tenant(company).get(wedding=wedding)
            total_spent = budget.total_overall_spent
            total_est = budget.total_estimated
            if total_est > 0:
                pct: float = float(total_spent) / float(total_est) * 100
                budget_pct = min(100.0, round(pct, 1))
            else:
                budget_pct = 0.0
        except Budget.DoesNotExist:
            budget_pct = 0.0
            logger.warning("Budget not found for wedding %s", wedding_uuid)

        # Tasks
        tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
        tasks_total = tasks.count()
        tasks_completed = tasks.filter(is_completed=True).count()

        # Contracts
        contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
        contracts_total = contracts.exclude(
            status=Contract.StatusChoices.CANCELED,
        ).count()
        contracts_signed = contracts.filter(
            status=Contract.StatusChoices.SIGNED,
        ).count()

        # Installments (non-PAID, upcoming 30 days + overdue)
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

        upcoming_installments = [
            {
                "uuid": inst.uuid,
                "installment_number": inst.installment_number,
                "amount": str(inst.amount),
                "due_date": inst.due_date,
                "status": inst.status,
            }
            for inst in installments
        ]

        # Urgent tasks (incomplete, due_date <= today or null, up to 3)
        urgent = tasks.filter(is_completed=False).order_by("due_date")[:3]
        urgent_tasks = [
            {
                "uuid": t.uuid,
                "title": t.title,
                "due_date": t.due_date,
            }
            for t in urgent
        ]

        # Categories summary (annotate to avoid N+1)
        categories = (
            BudgetCategory.objects.for_tenant(company)
            .filter(wedding=wedding)
            .select_related("budget")
            .annotate(_total_spent=Coalesce(Sum("expenses__actual_amount"), 0.0))
        )

        categories_summary = []
        for cat in categories:
            spent = float(cat._total_spent)
            alloc = float(cat.allocated_budget)
            pct = round(spent / alloc * 100) if alloc > 0 else 0
            categories_summary.append(
                {
                    "name": cat.name,
                    "allocated": str(cat.allocated_budget),
                    "spent": str(spent),
                    "percentage": min(pct, 100),
                }
            )

        return {
            "days_until_wedding": days_until,
            "budget_percentage_used": budget_pct,
            "tasks_completed": tasks_completed,
            "tasks_total": tasks_total,
            "contracts_signed": contracts_signed,
            "contracts_total": contracts_total,
            "upcoming_installments": upcoming_installments,
            "urgent_tasks": urgent_tasks,
            "categories_summary": categories_summary,
        }
