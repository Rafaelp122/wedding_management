"""
Selectors para o domínio de casamentos (Weddings).
Consultas otimizadas e encapsuladas de leitura para Wedding.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol, cast
from uuid import UUID

from django.db.models import Count

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.finances.models import Budget, Installment
from apps.logistics.models import Contract
from apps.weddings.models import Wedding
from apps.weddings.schemas import (
    WeddingDashboardCategoryOut,
    WeddingDashboardInstallmentOut,
    WeddingDashboardOut,
    WeddingDashboardTaskOut,
    WeddingOut,
    WeddingOverviewOut,
    WeddingStatusEnum,
)


if TYPE_CHECKING:
    from apps.tenants.models import Company
    from apps.weddings.managers import WeddingQuerySet


class _BudgetCategorySummary(Protocol):
    """Linha de categoria anotada por ``BudgetCategoryQuerySet.with_total_spent()``."""

    name: str
    allocated_budget: Decimal
    _total_spent: Decimal


def _list_categories_with_total_spent(
    company: Company, budget: Budget | None
) -> Iterable[_BudgetCategorySummary]:
    """
    Lista categorias do orçamento com ``_total_spent`` anotado.

    Args:
        company: O tenant atual para isolamento de dados.
        budget: Orçamento do casamento; ``None`` retorna iterável vazio.

    Returns:
        Iterável das categorias com os campos anotados pelo queryset.
    """
    from apps.finances.models import BudgetCategory

    if not budget:
        return cast(
            Iterable[_BudgetCategorySummary],
            BudgetCategory.objects.none(),
        )
    return cast(
        Iterable[_BudgetCategorySummary],
        BudgetCategory.objects.for_tenant(company)
        .with_total_spent()
        .filter(budget=budget),
    )


def wedding_list_selector(
    *,
    company: Company,
    search: str = "",
    status: str = "",
) -> WeddingQuerySet:
    """
    Lista os casamentos da empresa com filtros de texto/status e métricas anotadas.

    Args:
        company: O tenant atual para isolamento de dados.
        search: Termo de busca para filtrar por noivos ou local.
        status: Filtro por status do casamento (ex: IN_PROGRESS).

    Returns:
        WeddingQuerySet com casamentos filtrados e anotados com total_budget,
        overdue_installments e incomplete_tasks.
    """
    return (
        Wedding.objects.for_tenant(company)
        .select_related("company")
        .search(search)
        .by_status(status)
        .with_metrics()
    )


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
    return Wedding.objects.for_tenant(company).only_lookup()


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


def critical_weddings_selector(
    *,
    company: Company,
    today: date,
    limit: int = 5,
) -> WeddingQuerySet:
    """
    Retorna os casamentos em andamento nos próximos 90 dias com métricas críticas.

    Args:
        company: O tenant atual para isolamento de dados.
        today: Data de referência para cálculo dos prazos e métricas.
        limit: Quantidade máxima de registros retornados (padrão: 5).

    Returns:
        WeddingQuerySet com casamentos ordenados por data e anotados com
        métricas críticas.
    """
    return (
        Wedding.objects.for_tenant(company)
        .by_status(Wedding.StatusChoices.IN_PROGRESS)
        .upcoming(today=today, days=90)
        .with_critical_metrics(today=today)
        .order_by("date")[:limit]
    )


def wedding_overview_detail_selector(
    *,
    company: Company,
    uuid: UUID | str,
) -> WeddingOverviewOut:
    """
    Retorna visão geral detalhada do casamento com métricas agregadas.

    Busca dados de orçamento, tarefas, contratos e parcelas do casamento
    para compor a resposta completa utilizada na tela de detalhes.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: UUID do casamento a ser consultado.

    Returns:
        WeddingOverviewOut contendo dados do casamento e métricas de visão geral.

    Raises:
        ObjectNotFoundError: Se o casamento não existir ou pertencer a outro tenant.
    """
    wedding = wedding_get_selector(company=company, uuid=uuid)

    today = date.today()
    days_until = max(0, (wedding.date - today).days) if wedding.date else 0

    from apps.finances.models import Budget
    from apps.scheduler.models import Task

    budget = (
        Budget.objects.for_tenant(company)
        .with_total_spent()
        .filter(wedding=wedding)
        .first()
    )
    total_estimated = budget.total_estimated if budget else 0.0
    total_spent = getattr(budget, "_total_overall_spent", 0) if budget else 0.0
    budget_pct = (
        round((float(total_spent) / float(total_estimated)) * 100, 1)
        if total_estimated > 0
        else 0.0
    )

    categories_list = _list_categories_with_total_spent(company, budget)
    categories_summary = [
        WeddingDashboardCategoryOut(
            name=cat.name,
            allocated=str(cat.allocated_budget),
            spent=str(cat._total_spent),
            percentage=(
                round(
                    float(cat._total_spent) / float(cat.allocated_budget) * 100,
                    1,
                )
                if cat.allocated_budget and float(cat.allocated_budget) > 0
                else 0.0
            ),
        )
        for cat in categories_list
    ]

    tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
    tasks_total = tasks.count()
    tasks_completed = tasks.filter(is_completed=True).count()
    urgent_tasks_qs = tasks.filter(is_completed=False, due_date__lte=today).order_by(
        "due_date"
    )[:5]
    urgent_tasks_out = [
        WeddingDashboardTaskOut(uuid=t.uuid, title=t.title, due_date=t.due_date)
        for t in urgent_tasks_qs
    ]
    incomplete_tasks = tasks.filter(is_completed=False).count()

    contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
    contracts_total = contracts.count()
    contracts_signed = contracts.filter(status=Contract.StatusChoices.SIGNED).count()

    installments = (
        Installment.objects.for_tenant(company)
        .filter(
            wedding=wedding,
            status__in=[
                Installment.StatusChoices.PENDING,
                Installment.StatusChoices.OVERDUE,
            ],
        )
        .order_by("due_date")[:10]
    )
    upcoming_out = [
        WeddingDashboardInstallmentOut(
            uuid=i.uuid,
            installment_number=i.installment_number,
            amount=str(i.amount),
            due_date=i.due_date,
            status=i.status,
        )
        for i in installments
    ]
    overdue_count = (
        Installment.objects.for_tenant(company)
        .filter(wedding=wedding, status=Installment.StatusChoices.OVERDUE)
        .count()
    )

    wedding_out = WeddingOut(
        uuid=wedding.uuid,
        groom_name=wedding.groom_name,
        bride_name=wedding.bride_name,
        date=wedding.date,
        location=wedding.location,
        expected_guests=wedding.expected_guests,
        status=(
            WeddingStatusEnum(wedding.status)
            if isinstance(wedding.status, str)
            else WeddingStatusEnum(wedding.status.value)
        ),
        template=wedding.template,
        created_at=wedding.created_at,
        updated_at=wedding.updated_at,
        total_budget=(
            Decimal(str(total_estimated)) if total_estimated is not None else None
        ),
        overdue_installments=overdue_count,
        incomplete_tasks=incomplete_tasks,
    )

    return WeddingOverviewOut(
        wedding=wedding_out,
        overview=WeddingDashboardOut(
            days_until_wedding=days_until,
            budget_percentage_used=budget_pct,
            tasks_completed=tasks_completed,
            tasks_total=tasks_total,
            contracts_signed=contracts_signed,
            contracts_total=contracts_total,
            upcoming_installments=upcoming_out,
            urgent_tasks=urgent_tasks_out,
            categories_summary=categories_summary,
        ),
    )
