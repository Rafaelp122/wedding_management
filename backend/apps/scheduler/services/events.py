import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
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
    def list(
        user: AuthContextUser, wedding_id: UUID | str | None = None
    ) -> QuerySet[Event]:
        qs = Event.objects.for_user(user).select_related("wedding", "planner")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

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

        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
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

        event = Event(planner=planner, wedding=wedding, **data)
        event.save()

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

        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Evento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, uuid: UUID | str, data: dict[str, Any]
    ) -> Event:
        instance = EventService.get(user, uuid)
        return EventService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, uuid: UUID | str) -> None:
        instance = EventService.get(user, uuid)
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
