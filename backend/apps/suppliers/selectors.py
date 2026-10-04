"""Selectors de leitura para o domínio de fornecedores (apps.suppliers)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.suppliers.models import Supplier


if TYPE_CHECKING:
    from apps.suppliers.managers import SupplierQuerySet
    from apps.tenants.models import Company


def supplier_list_selector(
    company: Company,
    search: str = "",
    is_active: bool | None = None,
) -> SupplierQuerySet:
    """Lista fornecedores do tenant com contagem agregada de contratos.

    Aplica anotação 'with_contracts_count' e filtros opcionais de texto e status.

    Args:
        search: Termo para busca textual em nome, e-mail, telefone ou CNPJ.
        is_active: Filtro por status ativo/inativo.

    Returns:
        QuerySet de fornecedores anotado com a contagem de contratos.
    """
    qs = Supplier.objects.for_tenant(company).with_contracts_count()
    if search:
        qs = qs.search(search)
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    return qs


def supplier_get_selector(company: Company, uuid: UUID | str) -> Supplier:
    """Recupera um fornecedor específico por identificador único no tenant.

    Returns:
        Instância do fornecedor localizado.

    Raises:
        ObjectNotFoundError: Se o fornecedor não for encontrado ou não pertencer ao tenant.
    """
    return get_object_or_404_for_tenant(
        Supplier,
        company,
        uuid,
        detail="Fornecedor não encontrado ou acesso negado.",
        code="supplier_not_found_or_denied",
    )
