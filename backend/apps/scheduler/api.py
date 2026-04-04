from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.schemas import EventIn, EventOut, EventPatchIn
from apps.scheduler.services import EventService


# --- ROUTERS ---
router = Router(tags=["Scheduler"])


@router.get("/", response=list[EventOut], operation_id="scheduler_events_list")
@paginate
def list_events(request: HttpRequest):
    """
    Lista todos os eventos do cronograma do Planner logado.

    Retorna tanto tarefas isoladas quanto eventos atrelados aos diferentes casamentos.
    Garante que o usuário veja apenas os eventos de sua propriedade.
    """
    return EventService.list(request.user)


@router.get(
    "/{uuid}/",
    response={200: EventOut, **READ_ERROR_RESPONSES},
    operation_id="scheduler_events_read",
)
def get_event(request: HttpRequest, uuid: UUID4):
    """
    Retorna os detalhes completos de um evento específico no cronograma.

    Realiza a busca pelo UUID garantindo que o evento pertence ao Planner logado.
    """
    return EventService.get(request.user, uuid)


@router.post(
    "/",
    response={201: EventOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_create",
)
def create_event(request: HttpRequest, payload: EventIn):
    """
    Adiciona um novo evento ou tarefa ao cronograma.

    O Service realiza validações como:
    - Garantir que a data de término não seja anterior à data de início.
    - Validar os minutos para o disparo de lembretes (reminder).
    """
    return 201, EventService.create(request.user, payload.dict())


@router.patch(
    "/{uuid}/",
    response={200: EventOut, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_partial_update",
)
def partial_update_event(request: HttpRequest, uuid: UUID4, payload: EventPatchIn):
    """
    Atualiza informações específicas de um evento do cronograma.

    Permite adiar prazos, trocar descrições ou gerenciar lembretes para um evento.
    """
    instance = EventService.get(request.user, uuid)
    return EventService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="scheduler_events_delete",
)
def delete_event(request: HttpRequest, uuid: UUID4):
    """
    Remove um compromisso ou evento do cronograma.

    Deleta a tarefa permanentemente.
    Desativa também os alertas e lembretes associados a ela.
    """
    instance = EventService.get(request.user, uuid)
    EventService.delete(request.user, instance)
    return 204, None
