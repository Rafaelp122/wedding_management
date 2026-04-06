import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.scheduler.models import Event
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Garante isolamento total (Multitenancy), auditoria e integridade de agendamento.
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Event]:
        return Event.objects.for_user(user).select_related("wedding", "planner")

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Event:
        event = (
            Event.objects.for_user(user)
            .select_related("wedding", "planner")
            .filter(uuid=uuid)
            .first()
        )
        if event is None:
            raise ObjectNotFoundError(
                detail="Evento não encontrado ou acesso negado.",
                code="event_not_found_or_denied",
            )
        return event

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Event:
        planner = require_user(user)
        logger.info(f"Iniciando criação de Evento para planner_id={planner.id}")

        # 1. Resolução Segura de Dependências
        # O DRF pode enviar a instância já resolvida ou apenas o UUID. Tratamos ambos.
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                # Isolamento multitenant forçado na busca da dependência
                wedding = Wedding.objects.for_user(planner).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de agendamento em casamento inválido ou "
                    f"negado: {wedding_input} por planner_id={planner.id}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou você não tem permissão para "
                    "acessá-lo.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória (NÃO salva no banco ainda)
        event = Event(planner=planner, wedding=wedding, **data)

        # 3. Validação Estrita do Domínio
        # Aqui o Model garante que start_time < end_time e previne conflitos.
        event.save()

        # TODO (RF12): Integração com Celery para agendar notificações de lembrete
        # NotificationService.schedule_event_reminder(event)

        logger.info(
            f"Evento criado com sucesso: uuid={event.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return event

    @staticmethod
    @transaction.atomic
    def update(user: AuthContextUser, instance: Event, data: dict[str, Any]) -> Event:
        planner = require_user(user)
        logger.info(
            f"Atualizando Evento uuid={instance.uuid} por planner_id={planner.id}"
        )

        # Proteção contra sequestro de dados:
        # Impedimos que um evento seja movido para outro casamento/planner após criado.
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Validação estrita do Model para garantir que as novas datas não quebram regras
        instance.save()

        # TODO: Se as datas mudaram, reagendar a task no Celery

        logger.info(f"Evento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: Event, data: dict[str, Any]
    ) -> Event:
        return EventService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: Event) -> None:
        planner = require_user(user)
        logger.info(
            f"Tentativa de deleção do Evento uuid={instance.uuid} por "
            f"planner_id={planner.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Evento uuid={instance.uuid} DESTRUÍDO por planner_id={planner.id}"
            )

        except ProtectedError as e:
            logger.error(f"Falha de integridade ao deletar evento uuid={instance.uuid}")
            raise DomainIntegrityError(
                detail="Não é possível apagar este evento pois existem registros "
                "vinculados a ele.",
                code="event_protected_error",
            ) from e
