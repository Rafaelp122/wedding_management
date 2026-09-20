from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.scheduler.models import Event
from apps.scheduler.schemas import (
    EventIn,
    EventOut,
    EventPatchIn,
    SchedulerSummaryOut,
)
from apps.scheduler.selectors import (
    event_get_selector,
    event_list_selector,
    scheduler_summary_selector,
)
from apps.scheduler.services import EventService
from apps.users.types import AuthRequest


events_router = Router(tags=["Scheduler"])


@events_router.get("/", response=list[EventOut], operation_id="scheduler_events_list")
@paginate
def list_events(
    request: AuthRequest,
    wedding_id: UUID4 | None = None,
) -> QuerySet[Event]:
    """
    Lista todos os eventos do cronograma do Planner logado.

    Retorna tanto tarefas isoladas quanto eventos atrelados aos diferentes casamentos.
    Garante que o usuário veja apenas os eventos de sua propriedade.
    """
    user = request.user
    return event_list_selector(
        company=user.company,
        wedding_id=wedding_id,
    )


@events_router.get(
    "/summary/",
    response=SchedulerSummaryOut,
    operation_id="scheduler_summary_get",
)
def get_scheduler_summary(request: AuthRequest) -> dict[str, Any]:
    """
    Retorna o resumo estatístico consolidado dos eventos do cronograma.
    """
    return scheduler_summary_selector(company=request.user.company)


scheduler_router = Router(tags=["Scheduler"])


@scheduler_router.get(
    "/summary/",
    response=SchedulerSummaryOut,
    operation_id="scheduler_root_summary_get",
    include_in_schema=False,
)
def get_scheduler_root_summary(request: AuthRequest) -> dict[str, Any]:
    """
    Retorna o resumo consolidado de eventos (alias na raiz do scheduler).
    """
    return scheduler_summary_selector(company=request.user.company)


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
    user = request.user
    return event_get_selector(company=user.company, uuid=uuid)


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
    user = request.user
    created = EventService.create(user.company, payload)
    return 201, event_get_selector(company=user.company, uuid=created.uuid)


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
    user = request.user
    instance = event_get_selector(company=user.company, uuid=uuid)
    updated = EventService.update(user.company, instance, payload)
    return event_get_selector(company=user.company, uuid=updated.uuid)


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
    user = request.user
    instance = event_get_selector(company=user.company, uuid=uuid)
    EventService.delete(user.company, instance)
    return 204, None
