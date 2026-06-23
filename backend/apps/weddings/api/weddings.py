from collections.abc import Sequence

from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.users.auth import require_user
from apps.users.types import AuthRequest
from apps.weddings.models import Wedding
from apps.weddings.schemas import (
    WeddingByMonthOut,
    WeddingIn,
    WeddingOut,
    WeddingPatchIn,
)
from apps.weddings.services import WeddingService


router = Router(tags=["Weddings"])


@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
@paginate
def list_weddings(
    request: AuthRequest,
    search: str = "",
    status: str = "",
) -> QuerySet[Wedding]:
    user = require_user(request.user)
    return WeddingService.list(company=user.company, search=search, status=status)


@router.get(
    "/by-month/",
    response=list[WeddingByMonthOut],
    operation_id="weddings_by_month",
)
def list_weddings_by_month(
    request: AuthRequest,
    year: int,
) -> Sequence[dict]:
    """Retorna a quantidade de casamentos por mês no ano informado."""
    user = require_user(request.user)
    return WeddingService.count_by_month(company=user.company, year=year)


@router.get(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **READ_ERROR_RESPONSES},
    operation_id="weddings_read",
)
def retrieve_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    user = require_user(request.user)
    return WeddingService.get(company=user.company, uuid=uuid)


@router.post(
    "/",
    response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_create",
)
def create_wedding(request: AuthRequest, payload: WeddingIn) -> tuple[int, Wedding]:
    user = require_user(request.user)
    wedding = WeddingService.create(company=user.company, payload=payload)
    return 201, wedding


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
    user = require_user(request.user)
    instance = WeddingService.get(company=user.company, uuid=uuid)
    updated_wedding = WeddingService.update(
        company=user.company, instance=instance, payload=payload
    )
    return updated_wedding


@router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_delete",
)
def delete_wedding(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    user = require_user(request.user)
    instance = WeddingService.get(company=user.company, uuid=uuid)
    WeddingService.delete(company=user.company, instance=instance)
    return 204, None
