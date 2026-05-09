from ninja import Router
from pydantic import UUID4

from apps.core.constants import READ_ERROR_RESPONSES
from apps.users.types import AuthRequest
from apps.weddings.schemas import DashboardSummaryOut, WeddingDashboardOut
from apps.weddings.services import DashboardService


dashboard_router = Router(tags=["Dashboard"])


@dashboard_router.get(
    "/summary/",
    response={200: DashboardSummaryOut, **READ_ERROR_RESPONSES},
    operation_id="dashboard_summary",
)
def dashboard_summary(request: AuthRequest) -> dict:
    return DashboardService.get_summary(company=request.user.company)


@dashboard_router.get(
    "/wedding/{uuid}/",
    response={200: WeddingDashboardOut, **READ_ERROR_RESPONSES},
    operation_id="dashboard_wedding",
)
def wedding_dashboard(request: AuthRequest, uuid: UUID4) -> dict:
    return DashboardService.get_wedding_overview(
        company=request.user.company,
        wedding_uuid=uuid,
    )
