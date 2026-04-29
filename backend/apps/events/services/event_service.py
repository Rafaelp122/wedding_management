import logging
from typing import Any, Protocol, runtime_checkable
from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.users.types import AuthContextUser

from ..models import Event, WeddingDetail


logger = logging.getLogger(__name__)


@runtime_checkable
class EventTypeHandler(Protocol):
    """Protocolo que define como cada tipo de evento deve ser processado."""

    def create_details(self, event: Event, data: dict[str, Any]) -> None: ...
    def update_details(self, event: Event, data: dict[str, Any]) -> None: ...


class WeddingHandler:
    """Implementação especializada para Casamentos."""

    def create_details(self, event: Event, data: dict[str, Any]) -> None:
        detail_data = data.pop("wedding_detail", {})
        WeddingDetail.objects.create(event=event, **detail_data)

    def update_details(self, event: Event, data: dict[str, Any]) -> None:
        detail_data = data.pop("wedding_detail", None)
        if detail_data:
            WeddingDetail.objects.update_or_create(event=event, defaults=detail_data)


class EventService:
    """
    Orquestrador de Eventos (Strategy Pattern).
    Não usa herança estática. Delega para handlers baseados no tipo.
    """

    _handlers: dict[str, EventTypeHandler] = {
        Event.EventType.WEDDING: WeddingHandler(),
    }

    @classmethod
    def get_handler(cls, event_type: str) -> EventTypeHandler | None:
        return cls._handlers.get(event_type)

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Event]:
        """Listagem base genérica (sem JOINs)."""
        return Event.objects.for_user(user)

    @staticmethod
    def list_weddings(user: AuthContextUser) -> QuerySet[Event]:
        """Listagem especializada com detalhes de casamento pre-carregados."""
        return (
            Event.objects.for_user(user)
            .filter(event_type=Event.EventType.WEDDING)
            .prefetch_related("wedding_detail")
        )

    @staticmethod
    def resolve(user: AuthContextUser, uuid: Event | UUID | str) -> Event:
        """Resolve o evento e garante que detalhes 1:1 sejam carregados se existirem."""
        instance = Event.objects.resolve(user, uuid)
        if instance.event_type == Event.EventType.WEDDING:
            _ = getattr(instance, "wedding_detail", None)
        return instance

    @classmethod
    @transaction.atomic
    def create(cls, user: AuthContextUser, data: dict[str, Any]) -> Event:
        """Criação atômica e desacoplada."""
        if not user.is_authenticated or not user.company:
            raise BusinessRuleViolation(
                detail="Usuário sem empresa vinculada.", code="no_company"
            )

        event_type = data.get("event_type", Event.EventType.WEDDING)
        handler = cls.get_handler(event_type)

        # Remove campos que não pertencem ao modelo Event para evitar TypeError
        base_data = {
            k: v
            for k, v in data.items()
            if k
            in {"name", "event_type", "date", "location", "expected_guests", "status"}
        }

        event = Event(company=user.company, **base_data)

        try:
            event.save()
        except IntegrityError as e:
            raise BusinessRuleViolation(detail=str(e), code="db_integrity_error") from e

        if handler:
            handler.create_details(event, data)

        return event

    @classmethod
    @transaction.atomic
    def update(
        cls, user: AuthContextUser, instance: Event, data: dict[str, Any]
    ) -> Event:
        """Update inteligente e tipado."""
        handler = cls.get_handler(instance.event_type)

        # Regra de Negócio: Bloqueia conclusão de evento futuro
        new_status = data.get("status")
        if new_status == Event.StatusChoices.COMPLETED:
            from django.utils import timezone

            event_date = data.get("date") or instance.date
            if event_date > timezone.now().date():
                raise BusinessRuleViolation(
                    detail="Não pode marcar como CONCLUÍDO um evento em data futura.",
                    code="invalid_status_transition",
                )

        if handler:
            handler.update_details(instance, data)
            instance.refresh_from_db()

        allowed_fields = {"name", "date", "location", "expected_guests", "status"}
        for field in allowed_fields:
            if field in data:
                setattr(instance, field, data[field])

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Event) -> None:
        logger.warning(f"Deletando Evento uuid={instance.uuid}")
        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail=(
                    "Não é possível excluir o evento pois existem "
                    "contratos ou itens vinculados."
                ),
                code="event_protected_error",
            ) from e
