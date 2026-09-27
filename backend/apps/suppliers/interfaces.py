"""Fachada pública (Interface) do Bounded Context de Fornecedores (apps.suppliers).

Centraliza operações síncronas invocadas por outros contextos (ADR-031),
como contratos e logística.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import resolve_tenant_resource
from apps.suppliers.models import Supplier


if TYPE_CHECKING:
    from apps.tenants.models import Company


def get_supplier_for_company(
    *,
    company: Company,
    supplier_uuid_or_id: UUID | str | Supplier,
) -> Supplier:
    """Recupera um fornecedor validando o isolamento multitenant.

    Args:
        company: O tenant atual para isolamento de dados.
        supplier_uuid_or_id: UUID, identificador numérico ou instância de Supplier.

    Returns:
        Instância de Supplier pertencente à organização tenant.
    """
    return resolve_tenant_resource(
        Supplier,
        company,
        supplier_uuid_or_id,
        detail="Fornecedor inválido ou acesso negado.",
        code="supplier_not_found_or_denied",
    )


def list_active_suppliers_for_company(
    *,
    company: Company,
) -> list[Supplier]:
    """Lista todos os fornecedores ativos da organização tenant.

    Args:
        company: O tenant atual para isolamento de dados.

    Returns:
        Lista de instâncias ativas de Supplier.
    """
    return list(Supplier.objects.for_tenant(company).active().order_by("name"))


__all__ = [
    "get_supplier_for_company",
    "list_active_suppliers_for_company",
]
