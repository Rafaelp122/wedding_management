"""
Selectors para o domínio de casamentos (Weddings).
Consultas otimizadas e encapsuladas de leitura para Wedding.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import Count

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.weddings.models import Wedding


if TYPE_CHECKING:
    from apps.tenants.models import Company
    from apps.weddings.managers import WeddingQuerySet


def wedding_list_selector(
    *,
    company: Company,
    search: str = "",
    status: str = "",
) -> WeddingQuerySet:
    """
    Retorna o QuerySet encadeável de casamentos do tenant com filtros aplicados.

    Args:
        company: O tenant atual para isolamento de dados.
        search: Termo de busca para filtrar por noivos ou local.
        status: Filtro por status do casamento (ex: IN_PROGRESS).

    Returns:
        WeddingQuerySet com casamentos filtrados.
    """
    qs = Wedding.objects.for_tenant(company)
    return qs.select_related("company").search(search).by_status(status)


def wedding_get_selector(
    *,
    company: Company,
    uuid: UUID | str,
) -> Wedding:
    """
    Recupera um casamento específico pelo UUID garantindo o isolamento multitenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: O identificador único do casamento.

    Returns:
        A instância do casamento solicitada.

    Raises:
        ObjectNotFoundError: Se o casamento não existir ou pertencer a outro tenant.
    """
    return get_object_or_404_for_tenant(
        Wedding,
        company,
        uuid,
        select_related=["company"],
        code="wedding_not_found_or_denied",
    )


def wedding_lookup_selector(
    *,
    company: Company,
) -> WeddingQuerySet:
    """
    Retorna uma lista simplificada de casamentos para seleção rápida (comboboxes).

    Args:
        company: O tenant atual para isolamento de dados.

    Returns:
        WeddingQuerySet restrito aos campos uuid, bride_name e groom_name,
        ordenado por bride_name.
    """
    qs = Wedding.objects.for_tenant(company)
    return qs.only_lookup()


def wedding_count_by_month_selector(
    *,
    company: Company,
    year: int,
) -> Sequence[dict[str, int]]:
    """
    Agrupa e conta a quantidade de casamentos por mês para um determinado ano.

    Args:
        company: O tenant atual para isolamento de dados.
        year: O ano correspondente para filtragem dos casamentos.

    Returns:
        Sequência de dicionários com chaves 'month' e 'count',
        ordenada cronologicamente pelo mês.
    """
    qs = (
        Wedding.objects.for_tenant(company)
        .filter(date__year=year)
        .values("date__month")
        .annotate(count=Count("id"))
        .order_by("date__month")
    )
    return [{"month": item["date__month"], "count": item["count"]} for item in qs]
