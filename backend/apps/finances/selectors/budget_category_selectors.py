"""
Selectors de leitura para o domínio de Categorias Orçamentárias (BudgetCategory).
Consultas otimizadas e encapsuladas de leitura para BudgetCategory.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import BudgetCategory


if TYPE_CHECKING:
    from apps.finances.managers import BudgetCategoryQuerySet
    from apps.tenants.models import Company


def budget_category_list_selector(
    *,
    company: Company,
    budget_id: UUID | str | None = None,
    wedding_id: UUID | str | None = None,
) -> BudgetCategoryQuerySet:
    """
    Lista categorias de orçamento vinculadas ao tenant com filtros opcionais.

    Args:
        company: O tenant atual para isolamento de dados.
        budget_id: Identificador opcional do orçamento pai para filtragem.
        wedding_id: Identificador opcional do casamento para filtragem.

    Returns:
        BudgetCategoryQuerySet filtrado e anotado com o total pago por categoria.
    """
    qs: BudgetCategoryQuerySet = (
        BudgetCategory.objects.for_tenant(company)
        .with_total_spent()
        .select_related("budget", "wedding")
    )
    if budget_id:
        qs = qs.for_budget(budget_id)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs


def budget_category_get_selector(
    *,
    company: Company,
    uuid: UUID | str,
) -> BudgetCategory:
    """
    Recupera uma categoria de orçamento específica pelo UUID.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único da categoria de orçamento.

    Returns:
        A instância do BudgetCategory encontrada com total pago anotado.

    Raises:
        ObjectNotFoundError: Se a categoria não for encontrada ou
            não pertencer ao tenant.
    """
    try:
        return (
            BudgetCategory.objects.for_tenant(company)
            .with_total_spent()
            .select_related("budget", "wedding")
            .get(uuid=uuid)
        )
    except (BudgetCategory.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail="Categoria de orçamento não encontrada.",
            code="budget_category_not_found_or_denied",
        ) from e
