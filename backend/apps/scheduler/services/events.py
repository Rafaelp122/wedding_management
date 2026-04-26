import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.scheduler.models import Event


logger = logging.getLogger(__name__)


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Purificada: Recebe instâncias resolvidas ou usa resolvers internos.
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
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Event:
        from apps.core.dependencies import resolve_wedding_for_user

        planner = require_user(user)
        logger.info("Iniciando criação de Evento")

        wedding_input = data.pop("wedding")
        wedding = resolve_wedding_for_user(user, wedding_input)

        event = Event(planner=planner, wedding=wedding, **data)
        event.save()

        logger.info(f"Evento criado com sucesso: uuid={event.uuid}")
        return event

    @staticmethod
    @transaction.atomic
    def update(instance: Event, data: dict[str, Any]) -> Event:
        logger.info(f"Atualizando Evento uuid={instance.uuid}")

        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Event) -> None:
        logger.info(f"Deletando Evento uuid={instance.uuid}")

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar este evento pois existem registros "
                "vinculados a ele.",
                code="event_protected_error",
            ) from e
