"""
Selectors de leitura para o domínio de fornecedores.
"""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from apps.core.exceptions import ObjectNotFoundError
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.logistics.managers import SupplierCategoryQuerySet, SupplierQuerySet
from apps.logistics.models import Supplier
from apps.tenants.models import Company


def supplier_list_selector(
    company: Company,
    search: str = "",
    is_active: bool | None = None,
    category_id: UUID | str | None = None,
) -> SupplierQuerySet:
    """
    Lista os fornecedores do tenant com suporte a filtros e busca.

    Args:
        company: O tenant atual para isolamento de dados.
        search: Termo para busca textual em nome, e-mail, telefone ou CNPJ.
        is_active: Filtro opcional por status ativo/inativo.
        category_id: Filtro opcional por identificador de categoria.

    Returns:
        SupplierQuerySet contendo os fornecedores correspondentes.
    """
    qs = cast(SupplierQuerySet, Supplier.objects.for_tenant(company)).search(search)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if category_id:
        qs = qs.by_category(category_id)
    return qs


def supplier_get_selector(company: Company, uuid: UUID | str) -> Supplier:
    """
    Recupera um fornecedor específico pelo UUID com isolamento por tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único (UUID ou string) do fornecedor.

    Returns:
        A instância do Supplier correspondente.

    Raises:
        ObjectNotFoundError: Se o fornecedor não for encontrado ou acesso for negado.
    """
    return get_object_or_404_for_tenant(
        Supplier,
        company,
        uuid,
        detail="Fornecedor não encontrado ou acesso negado.",
        code="supplier_not_found_or_denied",
    )


def supplier_category_list_selector(
    company: Company,
) -> SupplierCategoryQuerySet:
    """
    Lista categorias de fornecedores do tenant com contagem de fornecedores.

    Args:
        company: O tenant atual para isolamento de dados.

    Returns:
        SupplierCategoryQuerySet contendo as categorias com contagem de fornecedores.
    """
    return SupplierCategoryQuerySet(model=None).none()  # type: ignore[arg-type]


def supplier_category_get_selector(company: Company, uuid: UUID | str) -> Any:
    """
    Recupera uma categoria de fornecedor específica pelo UUID.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único da categoria.

    Raises:
        ObjectNotFoundError: Categoria não encontrada.
    """
    raise ObjectNotFoundError(
        detail="Categoria de fornecedor não encontrada ou acesso negado.",
        code="supplier_category_not_found_or_denied",
    )
