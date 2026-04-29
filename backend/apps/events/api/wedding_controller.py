from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import ControllerBase, api_controller, http_get, http_patch, http_post
from ninja_extra.permissions import IsAuthenticated
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES

from ..schemas import WeddingIn, WeddingOut
from ..services.event_service import EventService


@api_controller("/events/weddings", tags=["Events"], permissions=[IsAuthenticated])
class WeddingController(ControllerBase):
    """
    CONTROLADOR ESPECIALIZADO DE CASAMENTOS.
    """

    @http_get(
        "/",
        response={200: list[WeddingOut], **READ_ERROR_RESPONSES},
        operation_id="events_list_weddings",
    )
    @paginate
    def list_weddings(self) -> QuerySet:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return EventService.list_weddings(self.context.request.user)

    @http_post(
        "/",
        response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="events_create_wedding",
    )
    def create_wedding(self, payload: WeddingIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, EventService.create(self.context.request.user, payload.model_dump())

    @http_patch(
        "/{event_uuid}/",
        response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="events_update_wedding",
    )
    def update_wedding(self, event_uuid: UUID4, payload: WeddingIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        instance = EventService.resolve(self.context.request.user, event_uuid)
        return EventService.update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )
