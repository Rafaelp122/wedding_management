import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.events.models import Event
from apps.scheduler.models import Appointment
from apps.users.auth import require_user
from apps.users.types import AuthContextUser


logger = logging.getLogger(__name__)


class AppointmentService:
    @staticmethod
    def list(
        user: AuthContextUser, event_id: UUID | str | None = None
    ) -> QuerySet[Appointment]:
        qs = Appointment.objects.for_user(user).select_related("event")
        if event_id:
            qs = qs.filter(event__uuid=event_id)
        return qs

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Appointment:
        planner = require_user(user)
        logger.info("Iniciando criação de Compromisso")

        event_input = data.pop("event", None)
        event = None
        if event_input:
            event = Event.objects.resolve(user, event_input)

        appointment = Appointment(company=planner.company, event=event, **data)
        appointment.save()

        logger.info("Compromisso criado com sucesso: uuid=%s", appointment.uuid)
        return appointment

    @staticmethod
    @transaction.atomic
    def update(instance: Appointment, data: dict[str, Any]) -> Appointment:
        logger.info("Atualizando Compromisso uuid=%s", instance.uuid)

        data.pop("event", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Appointment) -> None:
        logger.info("Deletando Compromisso uuid=%s", instance.uuid)
        instance.delete()
