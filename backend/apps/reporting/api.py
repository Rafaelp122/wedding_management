"""
Roteadores e endpoints para o módulo de reporting (dashboard e relatórios).
"""

import datetime
from typing import Any, Literal

from django.http import HttpResponse
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import READ_ERROR_RESPONSES
from apps.reporting.schemas import (
    CashFlowMonthOut,
    DashboardOperationsOut,
    DashboardSummaryOut,
    TaskProgressWeddingOut,
    WeddingDashboardOut,
)
from apps.reporting.selectors import (
    FinancialSummarySelector,
    TaskSummarySelector,
    dashboard_operations_selector,
    dashboard_summary_selector,
    wedding_overview_selector,
)
from apps.reporting.services import ReportGenerationService
from apps.users.types import AuthRequest


dashboard_router = Router(tags=["Dashboard"])
reports_router = Router(tags=["Reports"])


# ── Rotas de Dashboard ──
@dashboard_router.get(
    "/summary/",
    response={200: DashboardSummaryOut, **READ_ERROR_RESPONSES},
    operation_id="dashboard_summary",
)
def dashboard_summary(request: AuthRequest) -> dict[str, object]:
    """
    Retorna os KPIs agregados de desempenho para a empresa autenticada.

    Gera um DashboardSummaryOut contendo parcelas pendentes (próximos 7 dias),
    tarefas urgentes, parcelas atrasadas, contratos pendentes e casamentos críticos.
    """
    user = request.user
    return dashboard_summary_selector(company=user.company)


@dashboard_router.get(
    "/wedding/{uuid}/",
    response={200: WeddingDashboardOut, **READ_ERROR_RESPONSES},
    operation_id="dashboard_wedding",
)
def wedding_dashboard(request: AuthRequest, uuid: UUID4) -> dict[str, object]:
    """
    Retorna a visão detalhada de indicadores e métricas de um casamento.

    Gera um WeddingDashboardOut contendo contagem regressiva, percentual de
    uso do orçamento, estatísticas de tarefas e contratos, parcelas a vencer,
    tarefas urgentes e distribuição de despesas por categoria.
    """
    user = request.user
    return wedding_overview_selector(
        company=user.company,
        wedding_uuid=uuid,
    )


@dashboard_router.get(
    "/chart/cash-flow/",
    response={200: list[CashFlowMonthOut], **READ_ERROR_RESPONSES},
    operation_id="dashboard_chart_cash_flow",
)
def dashboard_chart_cash_flow(
    request: AuthRequest,
    year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Retorna o fluxo de caixa projetado mês a mês (parcelas pagas vs pendentes).

    Filtra as parcelas do tenant pelo ano especificado (padrão: ano corrente).
    """
    target_year = year if year is not None else datetime.date.today().year
    return FinancialSummarySelector.cash_flow_by_month(
        company=request.user.company,
        year=target_year,
    )


@dashboard_router.get(
    "/chart/task-progress/",
    response={200: list[TaskProgressWeddingOut], **READ_ERROR_RESPONSES},
    operation_id="dashboard_chart_task_progress",
)
def dashboard_chart_task_progress(
    request: AuthRequest,
    year: int | None = None,
) -> list[dict[str, Any]]:
    """
    Retorna o progresso percentual e contagem de tarefas dos casamentos.

    Ordenado pelo volume total de tarefas, com filtro opcional por ano do evento.
    """
    return TaskSummarySelector.tasks_progress_by_wedding(
        company=request.user.company,
        year=year,
    )


@dashboard_router.get(
    "/operations/",
    response={200: DashboardOperationsOut, **READ_ERROR_RESPONSES},
    operation_id="dashboard_operations_list",
)
def dashboard_operations(request: AuthRequest) -> dict[str, Any]:
    """
    Retorna o painel operacional consolidado com os Top 5 casamentos futuros,
    Top 5 tarefas urgentes e Top 5 contratos pendentes do tenant.
    """
    return dashboard_operations_selector(company=request.user.company)


# ── Rotas de Relatórios (Exportações) ──
@reports_router.get(
    "/weddings/{uuid}/",
    response=None,
    operation_id="reports_wedding_export",
)
def export_wedding_report(
    request: AuthRequest,
    uuid: UUID4,
    format: Literal["pdf", "excel"] = "pdf",
) -> HttpResponse:
    """
    Gera e exporta em fluxo binário o relatório consolidado do casamento.

    Retorna o arquivo binário com Content-Disposition correspondente ao formato.
    """
    file_bytes, content_type, filename = ReportGenerationService.export_wedding_report(
        company=request.user.company,
        wedding_uuid=uuid,
        report_format=format,
    )

    response = HttpResponse(file_bytes, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
