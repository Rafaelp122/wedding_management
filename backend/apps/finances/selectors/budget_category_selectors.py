"""Seletores de leitura para categorias orçamentárias (BudgetCategory)."""

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
    Lista categorias de orçamento vinculadas ao tenant com total gasto anotado.

    Otimiza a leitura utilizando select_related para 'budget' e 'wedding' e
    agrega o total pago via with_total_spent() (Coalesce/Sum).

    Returns:
        QuerySet de categorias orçamentárias anotado e filtrado.
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
    Recupera uma categoria de orçamento pelo identificador com total gasto anotado.

    Carrega as relações 'budget' e 'wedding' via select_related e agrega despesas pagas.

    Returns:
        A instância de categoria orçamentária encontrada.

    Raises:
        ObjectNotFoundError: Se a categoria não for encontrada ou não pertencer ao tenant.
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
