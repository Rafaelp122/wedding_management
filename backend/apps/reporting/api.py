"""
Roteadores e endpoints para o módulo de reporting (dashboard e relatórios).
"""

from typing import Literal

from django.http import HttpResponse
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import READ_ERROR_RESPONSES
from apps.reporting.schemas import (
    DashboardSummaryOut,
    ReportTaskQueuedOut,
    WeddingDashboardOut,
)
from apps.reporting.selectors import (
    dashboard_summary_selector,
    wedding_overview_selector,
)
from apps.reporting.services import ReportGenerationService
from apps.reporting.tasks import generate_wedding_report_task
from apps.users.types import AuthRequest
from apps.weddings.selectors import wedding_get_selector


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
    Gera e exporta em fluxo binário síncrono o relatório consolidado do casamento.

    Retorna o arquivo binário com Content-Disposition correspondente ao formato.
    """
    user = request.user
    company = user.company

    if format == "excel":
        file_bytes = ReportGenerationService.generate_wedding_excel(
            company=company,
            wedding_uuid=uuid,
        )
        content_type = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"relatorio-casamento-{uuid}.xlsx"
    else:
        file_bytes = ReportGenerationService.generate_wedding_pdf(
            company=company,
            wedding_uuid=uuid,
        )
        content_type = "application/pdf"
        filename = f"relatorio-casamento-{uuid}.pdf"

    response = HttpResponse(file_bytes, content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@reports_router.post(
    "/weddings/{uuid}/async/",
    response={202: ReportTaskQueuedOut, **READ_ERROR_RESPONSES},
    operation_id="reports_wedding_export_async",
)
def export_wedding_report_async(
    request: AuthRequest,
    uuid: UUID4,
    format: Literal["pdf", "excel"] = "pdf",
) -> tuple[int, dict[str, str]]:
    """
    Dispara a geração de relatório em background task (django.tasks).

    O arquivo é processado pelo worker, salvo no Cloudflare R2 / S3 e uma
    notificação in-app é enviada ao usuário com o link seguro de download.
    """
    user = request.user
    company = user.company

    # Validação prévia de isolamento multi-tenant
    wedding_get_selector(company=company, uuid=uuid)

    generate_wedding_report_task.enqueue(
        company_id=str(company.uuid),
        user_id=str(user.uuid),
        wedding_id=str(uuid),
        report_format=format,
    )

    fmt_label = format.upper()
    detail_msg = (
        f"Geração do relatório ({fmt_label}) iniciada em segundo plano. "
        "Você receberá uma notificação quando estiver pronto."
    )
    return 202, {
        "status": "enqueued",
        "detail": detail_msg,
    }
