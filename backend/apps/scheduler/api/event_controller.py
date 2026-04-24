from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.models import Event
from apps.scheduler.schemas import (
    EventIn,
    EventOut,
    EventPatchIn,
)
from apps.scheduler.services import EventService


@api_controller("/scheduler/events", tags=["Scheduler"])
class EventController(ControllerBase):
    def __init__(self, service: EventService):
        self.service = service

    @http_get("/", response=list[EventOut], operation_id="scheduler_events_list")
    @paginate
    def list_events(self, wedding_id: UUID4 | None = None) -> QuerySet[Event]:
        """
        Lista todos os eventos do cronograma do Planner logado.
        Pode ser filtrado por um casamento específico.
        """
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/{uuid}/",
        response={200: EventOut, **READ_ERROR_RESPONSES},
        operation_id="scheduler_events_read",
    )
    def retrieve_event(self, uuid: UUID4) -> Event:
        """
        Retorna detalhes de um evento específico.
        """
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: EventOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_create",
    )
    def create_event(self, payload: EventIn) -> tuple[int, Event]:
        """
        Cria um novo evento no cronograma.
        """
        event = self.service.create(self.context.request.user, payload.model_dump())
        return 201, event

    @http_patch(
        "/{uuid}/",
        response={200: EventOut, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_partial_update",
    )
    def partial_update_event(self, uuid: UUID4, payload: EventPatchIn) -> Event:
        """
        Atualiza parcialmente um evento.
        """
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="scheduler_events_delete",
    )
    def delete_event(self, uuid: UUID4) -> tuple[int, None]:
        """
        Remove um evento do cronograma.
        """
        self.service.delete(self.context.request.user, uuid)
        return 204, None
