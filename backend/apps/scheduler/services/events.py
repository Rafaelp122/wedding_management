import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    ObjectNotFoundError,
)
from apps.scheduler.models import Event
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Garante isolamento total (Multitenancy), auditoria e integridade de agendamento.
    """

    @staticmethod
    def list(company: Company, wedding_id: UUID | str | None = None) -> QuerySet[Event]:
        qs = Event.objects.for_tenant(company).select_related("wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Event:
        event = (
            Event.objects.for_tenant(company)
            .select_related("wedding")
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
    def create(
        company: Company,
        data: dict[str, Any],
        *,
        _caller_internal: bool = False,
    ) -> Event:
        logger.info(f"Iniciando criação de Evento para company_id={company.id}")

        wedding_input = data.pop("wedding", None)

        # BR-S01: Eventos de pagamento são gerados automaticamente
        if not _caller_internal and data.get("event_type") == Event.TypeChoices.PAYMENT:
            raise BusinessRuleViolation(
                detail=(
                    "Eventos de pagamento são gerados automaticamente e não podem "
                    "ser criados manualmente. Use o módulo financeiro para criar "
                    "despesas com parcelas."
                ),
                code="payment_event_readonly",
            )

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de agendamento em casamento inválido ou "
                    f"negado: {wedding_input} por company_id={company.id}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou você não tem permissão para "
                    "acessá-lo.",
                    code="wedding_not_found_or_denied",
                ) from e

        event = Event(company=company, wedding=wedding, **data)
        event.save()

        logger.info(
            f"Evento criado com sucesso: uuid={event.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return event

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Event, data: dict[str, Any]) -> Event:
        logger.info(
            f"Atualizando Evento uuid={instance.uuid} por company_id={company.id}"
        )

        # BR-S01: Eventos PAYMENT são read-only
        if instance.event_type == Event.TypeChoices.PAYMENT:
            raise BusinessRuleViolation(
                detail=(
                    "Eventos de pagamento são gerados automaticamente e não podem "
                    "ser editados manualmente. Acesse o módulo financeiro para ajustar."
                ),
                code="payment_event_readonly",
            )

        # BR-S01: Não é permitido alterar o tipo de um evento para PAYMENT
        if data.get("event_type") == Event.TypeChoices.PAYMENT:
            raise BusinessRuleViolation(
                detail=(
                    "Não é permitido alterar o tipo de um evento para 'pagamento'. "
                    "Eventos de pagamento são gerados automaticamente."
                ),
                code="payment_event_readonly",
            )

        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Evento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, uuid: UUID | str) -> None:
        instance = EventService.get(company, uuid)
        logger.info(
            f"Tentativa de deleção do Evento uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        # BR-S01: Eventos PAYMENT não podem ser deletados manualmente
        if instance.event_type == Event.TypeChoices.PAYMENT:
            raise BusinessRuleViolation(
                detail=(
                    "Eventos de pagamento são gerados automaticamente e não podem ser "
                    "deletados manualmente. Acesse o módulo financeiro para ajustar."
                ),
                code="payment_event_readonly",
            )

        instance.delete()
        logger.warning(
            f"Evento uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
        )
