from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES

from ..schemas import AnyEventOut, EventOut, EventPatchIn
from ..services.event_service import EventService


@api_controller("/events", tags=["Events"])
class EventController(ControllerBase):
    """
    CONTROLADOR GENÉRICO DE EVENTOS.

    Este controlador lida com operações que são comuns a TODOS os tipos de eventos
    (Casamentos, Corporativos, etc.), como listagem geral, busca por UUID e
    atualização de campos básicos (data, status, nome).

    Arquitetura: Utiliza o EventService para orquestrar a lógica de negócio.
    """

    @http_get(
        "/",
        response={200: list[EventOut], **READ_ERROR_RESPONSES},
        operation_id="events_list",
    )
    @paginate
    def list_events(self) -> QuerySet:
        """
        LISTAGEM GERAL (BASE):
        Retorna uma lista de todos os eventos da empresa (Tenant) sem os
        detalhes específicos. Ideal para visões de Dashboard, Calendário e
        Cronogramas onde a performance é prioridade.
        """
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return EventService.list(self.context.request.user)

    @http_get(
        "/{event_uuid}/",
        response={200: AnyEventOut, **READ_ERROR_RESPONSES},
        operation_id="events_retrieve",
    )
    def retrieve_event(self, event_uuid: UUID4):
        """
        DETALHE INDIVIDUAL (POLIMÓRFICO):
        Busca um evento específico. O retorno é polimórfico: se o evento
        for um Casamento, o JSON incluirá o objeto 'wedding_detail'.
        Se for genérico, retornará apenas a base.
        """
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return EventService.resolve(self.context.request.user, event_uuid)

    @http_patch(
        "/{event_uuid}/",
        response={200: EventOut, **MUTATION_ERROR_RESPONSES},
        operation_id="events_update_generic",
    )
    def update_event(self, event_uuid: UUID4, payload: EventPatchIn):
        """
        ATUALIZAÇÃO RASA (PATCH):
        Permite alterar campos que existem em qualquer evento
        (nome, data, local, status). Este endpoint ignora campos
        específicos de especializações (ex: nomes de noivos).
        """
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        instance = EventService.resolve(self.context.request.user, event_uuid)
        return EventService.update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{event_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="events_delete",
    )
    def delete_event(self, event_uuid: UUID4):
        """
        EXCLUSÃO DEFINITIVA:
        Remove o evento e todos os seus dados vinculados (detalhes, orçamentos, tarefas)
        através de CASCADE no banco de dados. Operação irreversível.
        """
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        instance = EventService.resolve(self.context.request.user, event_uuid)
        EventService.delete(instance)
        return 204, None
