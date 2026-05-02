from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.models import Event
from apps.scheduler.schemas import EventIn, EventOut, EventPatchIn
from apps.scheduler.services import EventService
from apps.users.auth import require_user
from apps.users.types import AuthRequest


events_router = Router(tags=["Scheduler"])


@events_router.get("/", response=list[EventOut], operation_id="scheduler_events_list")
@paginate
def list_events(
    request: AuthRequest, wedding_id: UUID4 | None = None
) -> QuerySet[Event]:
    """
    Lista todos os eventos do cronograma do Planner logado.

    Retorna tanto tarefas isoladas quanto eventos atrelados aos diferentes casamentos.
    Garante que o usuário veja apenas os eventos de sua propriedade.
    """
    user = require_user(request.user)
    return EventService.list(user.company, wedding_id=wedding_id)


@events_router.get(
    "/{uuid}/",
    response={200: EventOut, **READ_ERROR_RESPONSES},
    operation_id="scheduler_events_read",
)
def get_event(request: AuthRequest, uuid: UUID4) -> Event:
    """
    Retorna os detalhes completos de um evento específico no cronograma.

    Realiza a busca pelo UUID garantindo que o evento pertence ao Planner logado.
    """
    user = require_user(request.user)
    return EventService.get(user.company, uuid)


@events_router.post(
    "/",
    response={201: EventOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_create",
)
def create_event(request: AuthRequest, payload: EventIn) -> tuple[int, Event]:
    """
    Adiciona um novo evento ou tarefa ao cronograma.

    O Service realiza validações como:
    - Garantir que a data de término não seja anterior à data de início.
    - Validar os minutos para o disparo de lembretes (reminder).
    """
    user = require_user(request.user)
    return 201, EventService.create(user.company, payload.dict())


@events_router.patch(
    "/{uuid}/",
    response={200: EventOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_update",
)
def update_event(request: AuthRequest, uuid: UUID4, payload: EventPatchIn) -> Event:
    """
    Atualiza informações específicas de um evento do cronograma.

    Permite adiar prazos, trocar descrições ou gerenciar lembretes para um evento.
    """
    user = require_user(request.user)
    instance = EventService.get(user.company, uuid)
    return EventService.update(user.company, instance, payload.dict(exclude_unset=True))


@events_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_delete",
)
def delete_event(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove um compromisso ou evento do cronograma.

    Deleta a tarefa permanentemente.
    Desativa também os alertas e lembretes associados a ela.
    """
    user = require_user(request.user)
    EventService.delete(user.company, uuid)
    return 204, None
