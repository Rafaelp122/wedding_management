import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.scheduler.models import Event
from apps.scheduler.schemas import EventIn, EventPatchIn
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
        """
        Lista todos os eventos vinculados ao tenant (Company).

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: UUID ou string identificadora do casamento
                (opcional, para filtragem).

        Returns:
            QuerySet contendo os eventos filtrados da empresa.
        """
        qs = Event.objects.for_tenant(company).select_related("wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Event:
        """
        Recupera um evento específico pelo seu UUID, garantindo o tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: O identificador único do evento.

        Returns:
            A instância do Event localizado.

        Raises:
            ObjectNotFoundError: Se o evento não for encontrado ou pertencer
                a outro tenant.
        """
        return get_object_or_404_for_tenant(
            Event,
            company,
            uuid,
            select_related=["wedding"],
            code="event_not_found_or_denied",
        )

    @staticmethod
    @transaction.atomic
    def create(
        company: Company,
        payload: EventIn | dict[str, Any],
        *,
        _caller_internal: bool = False,
    ) -> Event:
        """
        Cria um novo evento para o tenant especificado.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do evento (EventIn ou dict).
            _caller_internal: Flag interna indicando se a chamada foi originada
                por outro serviço do sistema (permite bypass de regras de negócio).

        Returns:
            O evento criado e salvo no banco de dados.

        Raises:
            BusinessRuleViolation: Se for tentada a criação manual de um evento
                de pagamento (_caller_internal=False).
            ObjectNotFoundError: Se o casamento associado não for encontrado ou
                pertencer a outro tenant.
        """
        logger.info(f"Iniciando criação de Evento para company_id={company.id}")

        if isinstance(payload, dict):
            data = payload
        else:
            data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)

        if not _caller_internal:
            data.pop("source_installment", None)

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
            wedding = validate_tenant_ownership(
                company,
                wedding_input,
                detail="Acesso negado ao casamento.",
                code="wedding_not_found_or_denied",
            )
        else:
            wedding = get_object_or_404_for_tenant(
                Wedding,
                company,
                wedding_input,
                code="wedding_not_found_or_denied",
                detail="Acesso negado ao casamento.",
            )

        event = Event(company=company, wedding=wedding, **data)
        event.save()

        logger.info(
            f"Evento criado com sucesso: uuid={event.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return event

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Event, payload: EventPatchIn) -> Event:
        """
        Atualiza as informações de um evento existente.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do evento a ser atualizada.
            payload: Dados com as alterações a serem aplicadas.

        Returns:
            A instância do evento atualizada.

        Raises:
            ObjectNotFoundError: Se o evento pertencer a outro tenant.
            BusinessRuleViolation: Se o evento for de pagamento ou se for
                tentada a alteração do tipo para pagamento.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Evento não encontrado ou acesso negado.",
            code="event_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Evento uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

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
    def delete(company: Company, instance: Event) -> None:
        """
        Exclui um evento existente.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do evento a ser excluída.

        Raises:
            ObjectNotFoundError: Se o evento pertencer a outro tenant.
            BusinessRuleViolation: Se o evento for do tipo pagamento.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Evento não encontrado ou acesso negado.",
            code="event_not_found_or_denied",
        )
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
