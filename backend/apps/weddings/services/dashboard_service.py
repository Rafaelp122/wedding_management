import logging
from datetime import date, timedelta
from typing import Any
from uuid import UUID

from django.db.models import Count, OuterRef, Subquery
from django.db.models.functions import Coalesce

from apps.finances.models import Installment
from apps.scheduler.models import Task
from apps.tenants.models import Company
from apps.weddings.models import Wedding
from apps.weddings.services.summaries import (
    ContractSummaryService,
    FinancialSummaryService,
    TaskSummaryService,
)
from apps.weddings.services.wedding_service import WeddingService


logger = logging.getLogger(__name__)


class DashboardService:
    """
    Serviço para consolidação de dados e métricas do painel do usuário (Dashboard).

    Agrupa dados financeiros, tarefas pendentes, contratos e casamentos
    críticos em um único ponto de consulta para exibição no frontend.
    """

    @staticmethod
    def get_summary(company: Company) -> dict[str, Any]:
        """
        Gera um resumo consolidado de indicadores importantes para a empresa.

        Busca estatísticas financeiras gerais (parcelas a vencer e atrasadas),
        quantidade de tarefas urgentes, contratos pendentes e uma listagem
        de casamentos críticos ocorrendo nos próximos 90 dias com pendências.

        Args:
            company: O tenant atual para isolamento de dados.

        Returns:
            Dicionário contendo as chaves:
                - pending_installments_7d (str): Valor pendente em 7 dias.
                - urgent_tasks_count (int): Tarefas urgentes acumuladas.
                - overdue_installments_amount (str): Valor total em atraso.
                - overdue_installments_count (int): Quantidade de parcelas em atraso.
                - pending_contracts_count (int): Quantidade de contratos pendentes.
                - critical_weddings (list[dict]): Lista dos top 5 casamentos críticos.
        """
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
                incomplete_tasks=Coalesce(
                    Subquery(
                        Task.objects.filter(
                            wedding=OuterRef("pk"),
                            company=OuterRef("company"),
                            is_completed=False,
                        )
                        .values("wedding")
                        .annotate(cnt=Count("id"))
                        .values("cnt")[:1]
                    ),
                    0,
                ),
                pending_installments=Coalesce(
                    Subquery(
                        Installment.objects.filter(
                            wedding=OuterRef("pk"),
                            company=OuterRef("company"),
                            status=Installment.StatusChoices.PENDING,
                        )
                        .values("wedding")
                        .annotate(cnt=Count("id"))
                        .values("cnt")[:1]
                    ),
                    0,
                ),
                overdue_tasks=Coalesce(
                    Subquery(
                        Task.objects.filter(
                            wedding=OuterRef("pk"),
                            company=OuterRef("company"),
                            is_completed=False,
                            due_date__lt=today,
                        )
                        .values("wedding")
                        .annotate(cnt=Count("id"))
                        .values("cnt")[:1]
                    ),
                    0,
                ),
                overdue_installments=Coalesce(
                    Subquery(
                        Installment.objects.filter(
                            wedding=OuterRef("pk"),
                            company=OuterRef("company"),
                            status=Installment.StatusChoices.OVERDUE,
                        )
                        .values("wedding")
                        .annotate(cnt=Count("id"))
                        .values("cnt")[:1]
                    ),
                    0,
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
    def get_wedding_overview(company: Company, wedding_uuid: UUID) -> dict[str, Any]:
        """
        Computa uma visão geral detalhada de um casamento específico.

        Reúne métricas de cronômetro, uso do orçamento, progresso de tarefas,
        assinatura de contratos, parcelas financeiras a vencer, tarefas
        urgentes e resumo por categorias de despesa.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_uuid: O identificador único (UUID) do casamento.

        Returns:
            Dicionário com os indicadores detalhados do casamento solicitado.

        Raises:
            HttpError: Se o casamento correspondente ao UUID não for encontrado.
        """
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
