from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.users.types import AuthRequest
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingOut, WeddingPatchIn
from apps.weddings.services import WeddingService


router = Router(tags=["Weddings"])


@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
@paginate
def list_weddings(request: AuthRequest) -> QuerySet[Wedding]:
    return WeddingService.list(company=request.user.company)


@router.get(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **READ_ERROR_RESPONSES},
    operation_id="weddings_read",
)
def retrieve_wedding(request: AuthRequest, uuid: UUID4) -> Wedding:
    return WeddingService.get(company=request.user.company, uuid=uuid)


@router.post(
    "/",
    response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_create",
)
def create_wedding(request: AuthRequest, payload: WeddingIn) -> tuple[int, Wedding]:
    wedding = WeddingService.create(
        company=request.user.company, data=payload.model_dump()
    )
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
    data = payload.model_dump(exclude_unset=True)
    instance = WeddingService.get(company=request.user.company, uuid=uuid)
    updated_wedding = WeddingService.update(
        company=request.user.company, instance=instance, data=data
    )
    return updated_wedding


@router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_delete",
)
def delete_wedding(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    WeddingService.delete(company=request.user.company, uuid=uuid)
    return 204, None
