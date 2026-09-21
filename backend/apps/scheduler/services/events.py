import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils import timezone

from apps.core.exceptions import (
    BusinessRuleViolation,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.scheduler.models import Event
from apps.scheduler.schemas import EventIn, EventPatchIn, EventUpdateIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class EventService:
    """
    Camada de serviço para gestão de compromissos e calendário.
    Garante isolamento total (Multitenancy), auditoria e integridade de agendamento.

    Regras de Negócio e SSOT:
    - BR-S01 (Read-Only Guard de Pagamentos):
      docs/architecture/business-rules/scheduler/payment-event-readonly-guard.md
    - BR-S02 (Motor de Recorrência e Agendamento):
      docs/architecture/business-rules/scheduler/recurrence-rules-engine.md
    - BR-S03 (Detecção de Conflitos de Agenda):
      docs/architecture/business-rules/scheduler/schedule-conflict-validation.md
    - Hub do Domínio:
      docs/architecture/domains/scheduler-domain.md
    """

    @staticmethod
    def _validate_event_overlap(
        *,
        company: Company,
        wedding: Wedding,
        start_time: Any,
        end_time: Any,
        event_type: str,
        force_overlap: bool,
        instance: Event | None = None,
    ) -> None:
        if (
            event_type != Event.TypeChoices.PAYMENT
            and not force_overlap
            and end_time is not None
        ):
            overlap_qs = (
                Event.objects.for_tenant(company)
                .filter(
                    wedding=wedding,
                    start_time__lt=end_time,
                    end_time__gt=start_time,
                )
                .exclude(event_type=Event.TypeChoices.PAYMENT)
            )
            if instance is not None and instance.pk:
                overlap_qs = overlap_qs.exclude(pk=instance.pk)
            if overlap_qs.exists():
                raise BusinessRuleViolation(
                    "event_schedule_conflict",
                    message=(
                        "Existe outro compromisso agendado para este "
                        "horário no casamento."
                    ),
                )

    @staticmethod
    @transaction.atomic
    def create(
        company: Company,
        payload: EventIn | dict[str, Any],
        *,
        _caller_internal: bool = False,
        _allow_historical_start: bool = False,
    ) -> Event:
        """
        Cria um novo evento para o tenant especificado.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do evento (EventIn ou dict).
            _caller_internal: Flag interna indicando se a chamada foi originada
                por outro serviço do sistema para gerar eventos financeiros.
            _allow_historical_start: Permissão interna restrita à aplicação de
                templates com marcos anteriores à data atual.

        Returns:
            O evento criado e salvo no banco de dados.

        Raises:
            BusinessRuleViolation: Se o início estiver no passado ou for tentada
                a criação manual de um evento de pagamento
                (_caller_internal=False).
            ObjectNotFoundError: Se o casamento associado não for encontrado ou
                pertencer a outro tenant.
        """
        logger.info(f"Iniciando criação de Evento para company_id={company.id}")

        if isinstance(payload, dict):
            data = payload.copy()
            force_overlap = bool(data.pop("force_overlap", False))
        else:
            data = payload.model_dump(exclude_unset=True)
            force_overlap = bool(
                data.pop("force_overlap", getattr(payload, "force_overlap", False))
            )

        if (
            not _allow_historical_start
            and timezone.localdate(data["start_time"]) < timezone.localdate()
        ):
            raise BusinessRuleViolation(
                detail="A data e hora de início do evento não pode estar no passado.",
                code="event_start_time_in_past",
            )

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

        wedding = resolve_tenant_resource(
            Wedding,
            company,
            wedding_input,
            code="wedding_not_found_or_denied",
            detail="Acesso negado ao casamento.",
        )

        EventService._validate_event_overlap(
            company=company,
            wedding=wedding,
            start_time=data["start_time"],
            end_time=data.get("end_time"),
            event_type=data.get("event_type", Event.TypeChoices.OTHER),
            force_overlap=force_overlap,
        )

        event = Event(company=company, wedding=wedding, **data)
        event.save()

        logger.info(
            f"Evento criado com sucesso: uuid={event.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return event

    @staticmethod
    def _validate_update_payment_guards(instance: Event, data: dict[str, Any]) -> None:
        if instance.is_payment_event:
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

    @staticmethod
    def _apply_reminder_update(
        instance: Event, data: dict[str, Any], updated_fields: set[str]
    ) -> None:
        if "reminder_enabled" in data:
            rem_enabled = data.pop("reminder_enabled")
            if rem_enabled:
                rem_min = data.pop(
                    "reminder_minutes_before", instance.reminder_minutes_before
                )
                instance.enable_reminder(rem_min)
                updated_fields.add("reminder_minutes_before")
            else:
                instance.disable_reminder()
            updated_fields.add("reminder_enabled")

    @staticmethod
    @transaction.atomic
    def update(
        company: Company,
        instance: Event,
        payload: EventPatchIn | EventUpdateIn | dict[str, Any],
    ) -> Event:
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

        if isinstance(payload, dict):
            data = payload.copy()
            force_overlap = bool(data.pop("force_overlap", False))
            model_fields_set = set(data.keys())
        else:
            data = payload.model_dump(exclude_unset=True)
            force_overlap = bool(
                data.pop("force_overlap", getattr(payload, "force_overlap", False))
            )
            model_fields_set = payload.model_fields_set

        EventService._validate_update_payment_guards(instance, data)

        data.pop("wedding", None)
        data.pop("company", None)

        EventService._validate_event_overlap(
            company=company,
            wedding=instance.wedding,
            start_time=data.get("start_time", instance.start_time),
            end_time=data.get("end_time", instance.end_time),
            event_type=data.get("event_type", instance.event_type),
            force_overlap=force_overlap,
            instance=instance,
        )

        updated_fields: set[str] = set()

        if "start_time" in data or "end_time" in data:
            new_start = data.pop("start_time", instance.start_time)
            new_end = data.pop("end_time", instance.end_time)
            try:
                instance.reschedule(new_start, new_end)
            except DjangoValidationError as e:
                raise BusinessRuleViolation(
                    detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                    code="event_update_validation_error",
                ) from e
            if "start_time" in model_fields_set:
                updated_fields.add("start_time")
            if "end_time" in model_fields_set:
                updated_fields.add("end_time")

        EventService._apply_reminder_update(instance, data, updated_fields)

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            try:
                instance.save(update_fields=list(updated_fields))
            except DjangoValidationError as e:
                raise BusinessRuleViolation(
                    detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                    code="event_update_validation_error",
                ) from e

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
        if instance.is_payment_event:
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
