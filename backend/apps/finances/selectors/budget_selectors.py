"""
Selectors de leitura para o domínio de Orçamento (Budget).
Consultas otimizadas e encapsuladas de leitura para Budget.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import Avg

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Budget


if TYPE_CHECKING:
    from apps.finances.managers import BudgetQuerySet
    from apps.tenants.models import Company


def _attach_tenant_budget_metrics(budget: Budget, company: Company) -> None:
    """Calcula e anota a média do orçamento e percentual comparativo do tenant."""
    avg = Budget.objects.for_tenant(company).aggregate(avg=Avg("total_estimated"))[
        "avg"
    ]
    if avg is not None and not isinstance(avg, Decimal):
        avg = Decimal(str(avg))
    budget._tenant_average_budget = avg  # type: ignore[attr-defined]
    if avg and avg > Decimal("0.00") and budget.total_estimated is not None:
        budget._comparison_percentage = round(  # type: ignore[attr-defined]
            float(((budget.total_estimated - avg) / avg) * 100), 1
        )
    else:
        budget._comparison_percentage = None  # type: ignore[attr-defined]


def budget_list_selector(
    *,
    company: Company,
    wedding_id: UUID | str | None = None,
) -> BudgetQuerySet:
    """
    Lista os orçamentos pertencentes ao tenant com filtros opcionais
    e anotação de gasto total.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para filtragem.

    Returns:
        BudgetQuerySet filtrado e anotado com o gasto total calculado.
    """
    qs: BudgetQuerySet = (
        Budget.objects.for_tenant(company).with_total_spent().select_related("wedding")
    )
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs


def budget_get_selector(
    *,
    company: Company,
    uuid: UUID | str | None = None,
    wedding_id: int | UUID | str | None = None,
) -> Budget:
    """
    Recupera um orçamento específico pelo UUID ou pelo casamento com o
    total gasto anotado.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único do orçamento (opcional).
        wedding_id: ID primário ou UUID do casamento associado (opcional).

    Returns:
        A instância do Budget encontrada com total gasto anotado.

    Raises:
        ObjectNotFoundError: Se o orçamento não for encontrado ou
            não pertencer ao tenant.
        ValueError: Se nem uuid nem wedding_id forem informados.
    """
    if uuid is None and wedding_id is None:
        raise ValueError("É necessário informar uuid ou wedding_id.")

    try:
        qs = (
            Budget.objects.for_tenant(company)
            .with_total_spent()
            .select_related("wedding")
        )
        if uuid is not None:
            budget = qs.get(uuid=uuid)
        elif isinstance(wedding_id, int):
            budget = qs.get(wedding_id=wedding_id)
        elif wedding_id is not None:
            budget = qs.get(wedding__uuid=wedding_id)
        else:
            raise ValueError("É necessário informar uuid ou wedding_id.")
        _attach_tenant_budget_metrics(budget, company)
        return budget
    except (Budget.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        ) from e


def budget_get_for_wedding_selector(
    *,
    company: Company,
    wedding_uuid: UUID | str,
) -> Budget:
    """
    Recupera o orçamento de um casamento específico pelo UUID do casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_uuid: Identificador único do casamento.

    Returns:
        A instância do Budget vinculada ao casamento com total gasto anotado.

    Raises:
        ObjectNotFoundError: Se o orçamento não for encontrado para
            o casamento informado.
    """
    try:
        budget = (
            Budget.objects.for_tenant(company)
            .with_total_spent()
            .select_related("wedding")
            .get(wedding__uuid=wedding_uuid)
        )
        _attach_tenant_budget_metrics(budget, company)
        return budget
    except (Budget.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail="Orçamento não encontrado para o casamento informado.",
            code="budget_not_found_or_denied",
        ) from e
