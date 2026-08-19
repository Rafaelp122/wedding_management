from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import READ_ERROR_RESPONSES
from apps.reporting.schemas import DashboardSummaryOut, WeddingDashboardOut
from apps.reporting.selectors import (
    dashboard_summary_selector,
    wedding_overview_selector,
)
from apps.users.types import AuthRequest


dashboard_router = Router(tags=["Dashboard"])


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
