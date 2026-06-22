import logging
from datetime import date, timedelta
from uuid import UUID

from django.db.models import Count, Q

from apps.finances.models import Installment
from apps.tenants.models import Company
from apps.weddings.models import Wedding
from apps.weddings.services.contract_summary_service import ContractSummaryService
from apps.weddings.services.financial_summary_service import FinancialSummaryService
from apps.weddings.services.task_summary_service import TaskSummaryService
from apps.weddings.services.wedding_service import WeddingService


logger = logging.getLogger(__name__)


class DashboardService:
    @staticmethod
    def get_summary(company: Company) -> dict:
        logger.info(f"Computando resumo do dashboard para company_id={company.id}")
        today = date.today()

        pending_7d = FinancialSummaryService.pending_installments_7d(
            company=company, today=today
        )
        overdue_amount, overdue_count = FinancialSummaryService.overdue_installments(
            company=company, today=today
        )
        urgent_tasks_count = TaskSummaryService.urgent_tasks_count(
            company=company, today=today
        )
        pending_contracts_count = ContractSummaryService.pending_contracts_count(
            company=company
        )

        ninety_days = today + timedelta(days=90)
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

        logger.info(
            f"Dashboard resumo computado: company_id={company.id}, "
            f"critical_weddings={len(critical_weddings)}"
        )
        return {
            "pending_installments_7d": f"{pending_7d:.2f}",
            "urgent_tasks_count": urgent_tasks_count,
            "overdue_installments_amount": f"{overdue_amount:.2f}",
            "overdue_installments_count": overdue_count,
            "pending_contracts_count": pending_contracts_count,
            "critical_weddings": critical_weddings,
        }

    @staticmethod
    def get_wedding_overview(company: Company, wedding_uuid: UUID) -> dict:
        wedding = WeddingService.get(company, wedding_uuid)
        logger.info(
            f"Computando visão geral do casamento uuid={wedding_uuid} "
            f"para company_id={company.id}"
        )
        today = date.today()
        days_until = max(0, (wedding.date - today).days)

        budget_pct = FinancialSummaryService.budget_percentage_used(
            company=company, wedding=wedding
        )
        tasks_completed, tasks_total = TaskSummaryService.wedding_task_stats(
            company=company, wedding=wedding
        )
        contracts_signed, contracts_total = (
            ContractSummaryService.wedding_contract_stats(
                company=company, wedding=wedding
            )
        )
        upcoming_installments = FinancialSummaryService.upcoming_installments(
            company=company, wedding=wedding, today=today
        )
        urgent_tasks = TaskSummaryService.urgent_tasks(
            company=company, wedding=wedding, today=today
        )
        categories_summary = FinancialSummaryService.categories_summary(
            company=company, wedding=wedding
        )

        logger.info(
            f"Visão geral do casamento uuid={wedding_uuid} computada: "
            f"days_until={days_until}, budget_pct={budget_pct}"
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
