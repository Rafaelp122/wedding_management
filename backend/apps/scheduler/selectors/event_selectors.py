"""
Selectors para o domínio de Eventos (Calendário).
Consultas otimizadas e encapsuladas de leitura para Event.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

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
        select_related=["wedding"],
        code="event_not_found_or_denied",
    )
