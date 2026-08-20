"""
Selectors de leitura para o domínio de Orçamento (Budget).
Consultas otimizadas e encapsuladas de leitura para Budget.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Budget


if TYPE_CHECKING:
    from apps.finances.managers import BudgetQuerySet
    from apps.tenants.models import Company


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


def budget_get_selector(*, company: Company, uuid: UUID | str) -> Budget:
    """
    Recupera um orçamento específico pelo UUID com o total gasto anotado.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único do orçamento.

    Returns:
        A instância do Budget encontrada com total gasto anotado.

    Raises:
        ObjectNotFoundError: Se o orçamento não for encontrado ou
            não pertencer ao tenant.
    """
    try:
        return (
            Budget.objects.for_tenant(company)
            .with_total_spent()
            .select_related("wedding")
            .get(uuid=uuid)
        )
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
        return (
            Budget.objects.for_tenant(company)
            .with_total_spent()
            .select_related("wedding")
            .get(wedding__uuid=wedding_uuid)
        )
    except (Budget.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail="Orçamento não encontrado para o casamento informado.",
            code="budget_not_found_or_denied",
        ) from e
