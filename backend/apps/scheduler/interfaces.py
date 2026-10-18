"""
Fachada pública (Interface) do Bounded Context do Agendador (Scheduler).
Centraliza operações síncronas invocadas por outros contextos (ex: finances, weddings).
"""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING
from uuid import UUID

from django.db import transaction
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.schemas import EventIn
from apps.scheduler.services import EventService
from apps.scheduler.services.templates import get_template_events


if TYPE_CHECKING:
    from apps.finances.models import Expense, Installment
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding


@transaction.atomic
def create_payment_events_for_installments(
    *,
    company: Company,
    expense: Expense,
    installments: list[Installment],
) -> None:
    """
    Cria eventos de pagamento no calendário da agenda para cada parcela gerada.

    Regra de Negócio:
        BR-S01 (docs/architecture/business-rules/scheduler/payment-event-readonly-guard.md)

    Efeitos Colaterais:
        - Persiste instâncias de Event com tipo 'pagamento' e salvaguarda read-only (BR-S01).
    """
    total_installments = len(installments)
    for inst in installments:
        naive_start = datetime.combine(inst.due_date, time(hour=9, minute=0))
        event_start = timezone.make_aware(naive_start)
        EventService.create(
            company,
            {
                "wedding": expense.wedding,
                "title": (
                    f"Pagamento: {expense.name} - Parcela "
                    f"{inst.installment_number}/{total_installments}"
                ),
                "event_type": "pagamento",
                "start_time": event_start,
                "description": f"Valor: R$ {inst.amount:.2f} — {expense.name}",
                "source_installment": inst,
            },
            _caller_internal=True,
        )


@transaction.atomic
def delete_payment_events_for_expense(
    *,
    company: Company,
    expense: Expense,
) -> None:
    """
    Remove todos os eventos de pagamento do calendário vinculados a uma despesa.

    Efeitos Colaterais:
        - Exclui em lote os eventos do tipo pagamento relacionados às parcelas da despesa.
    """
    Event.objects.for_tenant(company).filter(
        wedding=expense.wedding,
        event_type="pagamento",
        source_installment__expense=expense,
    ).delete()


@transaction.atomic
def delete_payment_event_for_installment(
    *,
    company: Company,
    installment: Installment,
) -> None:
    """
    Remove o evento de pagamento do calendário vinculado a uma parcela específica.

    Efeitos Colaterais:
        - Exclui o evento correspondente à parcela informada.
    """
    Event.objects.for_tenant(company).filter(
        wedding=installment.expense.wedding,
        event_type="pagamento",
        source_installment=installment,
    ).delete()


@transaction.atomic
def apply_wedding_schedule_template(
    *,
    company: Company,
    wedding: Wedding,
    template_name: str,
) -> None:
    """
    Aplica template canônico de cronograma gerando eventos baseados na data do casamento.

    Calcula o deslocamento em dias a partir da data da cerimônia.

    Regra de Negócio:
        BR-W07 (docs/architecture/business-rules/weddings/wedding-schedule-templates.md)

    Efeitos Colaterais:
        - Persiste eventos na agenda com permissão de marcos históricos (_allow_historical_start=True).

    Args:
        template_name: Identificador canônico do template registrado.

    Raises:
        BusinessRuleViolation: Se o template informado não existir no registro do sistema.
    """
    template_events = get_template_events(template_name)

    for event_data in template_events:
        offset_days = int(event_data["offset_days"])
        naive_start = datetime.combine(
            wedding.date - timedelta(days=offset_days),
            time(hour=9, minute=0),
        )
        event_start = timezone.make_aware(naive_start)

        EventService.create(
            company,
            EventIn(
                wedding=wedding.uuid,
                title=event_data["title"],
                event_type=event_data["event_type"],
                start_time=event_start,
                location="",
                description="",
            ),
            _allow_historical_start=True,
        )


def enqueue_wedding_checklist_generation(
    *,
    company_id: int | str,
    wedding_uuid: UUID | str,
    template: str | None = None,
) -> None:
    """
    Enfileira a geração assíncrona do checklist operacional inicial do casamento.

    Efeitos Colaterais:
        - Enfileira a tarefa assíncrona generate_checklist_from_template_task (ADR-017 / RFC-001).

    Args:
        template: Nome opcional do template de cronograma para instanciar tarefas padrão.
    """
    from apps.scheduler.tasks import generate_checklist_from_template_task

    generate_checklist_from_template_task.enqueue(
        company_id,
        str(wedding_uuid),
        template,
    )


__all__ = [
    "apply_wedding_schedule_template",
    "create_payment_events_for_installments",
    "delete_payment_event_for_installment",
    "delete_payment_events_for_expense",
    "enqueue_wedding_checklist_generation",
]
