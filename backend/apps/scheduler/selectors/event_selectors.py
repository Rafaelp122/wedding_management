"""
Selectors para o domínio de Eventos (Calendário).
Consultas otimizadas e encapsuladas de leitura para Event.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

from django.utils import timezone

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.scheduler.managers import EventQuerySet
from apps.scheduler.models import Event


if TYPE_CHECKING:
    from apps.tenants.models import Company


def event_list_selector(
    *,
    company: Company,
    wedding_id: UUID | str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> EventQuerySet:
    """
    Lista eventos do calendário vinculados ao tenant, com filtros opcionais.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para filtragem.
        start_date: Data inicial opcional do intervalo de busca.
        end_date: Data final opcional do intervalo de busca.

    Returns:
        EventQuerySet com os eventos filtrados e ordenados cronologicamente.
    """
    qs = Event.objects.for_tenant(company).select_related("wedding", "company")
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if start_date is not None or end_date is not None:
        qs = qs.in_period(start_date, end_date)
    return qs.chronological()


def event_get_selector(*, company: Company, uuid: UUID | str) -> Event:
    """
    Recupera um evento específico pelo UUID, garantindo o isolamento multitenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: O identificador único do evento.

    Returns:
        A instância do Event encontrado.

    Raises:
        ObjectNotFoundError: Se o evento não existir ou pertencer a outro tenant.
    """
    return get_object_or_404_for_tenant(
        Event,
        company,
        uuid,
        select_related=["wedding", "company"],
        code="event_not_found_or_denied",
    )


def scheduler_summary_selector(*, company: Company) -> dict[str, Any]:
    """
    Retorna contagens e métricas consolidadas dos eventos do tenant.

    Args:
        company: O tenant atual para isolamento de dados.

    Returns:
        Dicionário com total, upcoming_7_days e with_reminder.
    """
    today = timezone.localdate()
    end_7_days = today + timedelta(days=7)
    tenant_events = Event.objects.for_tenant(company)

    total = tenant_events.count()
    upcoming_7_days = tenant_events.filter(
        start_time__date__gte=today,
        start_time__date__lte=end_7_days,
    ).count()
    with_reminder = tenant_events.filter(reminder_enabled=True).count()

    return {
        "total": total,
        "upcoming_7_days": upcoming_7_days,
        "with_reminder": with_reminder,
    }
