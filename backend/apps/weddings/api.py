from collections.abc import Sequence

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.reporting.selectors.summaries.wedding import WeddingSummarySelector
from apps.users.types import AuthRequest
from apps.weddings.models import Wedding
from apps.weddings.schemas import (
    WeddingByMonthOut,
    WeddingIn,
    WeddingLookupOut,
    WeddingOut,
    WeddingPatchIn,
)
from apps.weddings.selectors import (
    wedding_count_by_month_selector,
    wedding_get_selector,
    wedding_lookup_selector,
)
from apps.weddings.services import WeddingService


router = Router(tags=["Weddings"])


@router.get("/lookup/", response=list[WeddingLookupOut], operation_id="weddings_lookup")
def list_weddings_lookup(request: AuthRequest) -> QuerySet[Wedding]:
    """Retorna lista simplificada de casamentos para comboboxes."""
    user = request.user
    return wedding_lookup_selector(company=user.company)


@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
@paginate
def list_weddings(
    request: AuthRequest,
    search: str = "",
    status: str = "",
) -> QuerySet[Wedding]:
    user = request.user
    return WeddingSummarySelector.list_weddings_with_metrics(
        company=user.company, search=search, status=status
    )


@router.get(
    "/by-month/",
    response=list[WeddingByMonthOut],
    operation_id="weddings_by_month",
)
def list_weddings_by_month(
    request: AuthRequest,
    year: int,
) -> Sequence[dict[str, int]]:
    """Retorna a quantidade de casamentos por mês no ano informado."""
    user = request.user
    return wedding_count_by_month_selector(company=user.company, year=year)


@router.get(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **READ_ERROR_RESPONSES},
    operation_id="weddings_read",
)
def retrieve_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    user = request.user
    return wedding_get_selector(company=user.company, uuid=uuid)


@router.post(
    "/",
    response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_create",
)
def create_wedding(request: AuthRequest, payload: WeddingIn) -> tuple[int, Wedding]:
    user = request.user
    wedding = WeddingService.create(company=user.company, payload=payload)
    return 201, wedding_get_selector(company=user.company, uuid=wedding.uuid)


@router.patch(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_update",
)
def update_wedding(
    request: AuthRequest,
    uuid: UUID4,
    payload: WeddingPatchIn,
) -> Wedding:
    user = request.user
    instance = wedding_get_selector(company=user.company, uuid=uuid)
    WeddingService.update(company=user.company, instance=instance, payload=payload)
    return wedding_get_selector(company=user.company, uuid=uuid)


@router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_delete",
)
def delete_wedding(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    user = request.user
    instance = wedding_get_selector(company=user.company, uuid=uuid)
    WeddingService.delete(company=user.company, instance=instance)
    return 204, None


@router.post(
    "/{uuid:uuid}/complete/",
    response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_complete",
)
def complete_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    """Caso de uso: Conclui um casamento existente garantindo data válida."""
    user = request.user
    instance = wedding_get_selector(company=user.company, uuid=uuid)
    WeddingService.complete(company=user.company, instance=instance)
    return wedding_get_selector(company=user.company, uuid=uuid)


@router.post(
    "/{uuid:uuid}/cancel/",
    response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_cancel",
)
def cancel_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    """Caso de uso: Cancela um casamento em andamento."""
    user = request.user
    instance = wedding_get_selector(company=user.company, uuid=uuid)
    WeddingService.cancel(company=user.company, instance=instance)
    return wedding_get_selector(company=user.company, uuid=uuid)


@router.post(
    "/{uuid:uuid}/reopen/",
    response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_reopen",
)
def reopen_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    """
    Caso de uso: Reabre um casamento cancelado voltando para em andamento.
    """
    user = request.user
    instance = wedding_get_selector(company=user.company, uuid=uuid)
    WeddingService.reopen(company=user.company, instance=instance)
    return wedding_get_selector(company=user.company, uuid=uuid)
