"""Ninja Router para o domínio de fornecedores (apps.suppliers)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.suppliers.models import Supplier
from apps.suppliers.schemas import SupplierIn, SupplierOut, SupplierPatchIn
from apps.suppliers.selectors import supplier_get_selector, supplier_list_selector
from apps.suppliers.services import SupplierService
from apps.users.types import AuthRequest


if TYPE_CHECKING:
    from django.db.models import QuerySet


# Router canônico (/suppliers/)
suppliers_router = Router(tags=["Suppliers"])


# ── Canonical Endpoints (/suppliers/) ──────────────────────────────────────────


@suppliers_router.get("/", response=list[SupplierOut], operation_id="suppliers_list")
@paginate
def list_suppliers(
    request: AuthRequest,
    search: str = "",
    is_active: bool | None = None,
) -> QuerySet[Supplier]:
    """Lista todos os fornecedores cadastrados pelo tenant autenticado.

    Aceita filtros de busca textual e status ativo.
    """
    user = request.user
    return supplier_list_selector(
        company=user.company, search=search, is_active=is_active
    )


@suppliers_router.get(
    "/{uuid:uuid}/",
    response={200: SupplierOut, **READ_ERROR_RESPONSES},
    operation_id="suppliers_read",
)
def retrieve_supplier(request: AuthRequest, uuid: UUID4) -> Supplier:
    """Retorna os detalhes de um fornecedor específico."""
    user = request.user
    return supplier_get_selector(company=user.company, uuid=uuid)


@suppliers_router.post(
    "/",
    response={201: SupplierOut, **MUTATION_ERROR_RESPONSES},
    operation_id="suppliers_create",
)
def create_supplier(request: AuthRequest, payload: SupplierIn) -> tuple[int, Supplier]:
    """Cadastra um novo fornecedor no sistema."""
    user = request.user
    supplier = SupplierService.create(company=user.company, payload=payload)
    return 201, supplier


@suppliers_router.patch(
    "/{uuid:uuid}/",
    response={200: SupplierOut, **MUTATION_ERROR_RESPONSES},
    operation_id="suppliers_update",
)
def update_supplier(
    request: AuthRequest, uuid: UUID4, payload: SupplierPatchIn
) -> Supplier:
    """Atualiza informações específicas de um fornecedor (nome, contato, endereço, status)."""
    user = request.user
    supplier = supplier_get_selector(company=user.company, uuid=uuid)
    return SupplierService.update(
        company=user.company, instance=supplier, payload=payload
    )


@suppliers_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="suppliers_delete",
)
def delete_supplier(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """Remove o cadastro de um fornecedor do sistema."""
    user = request.user
    supplier = supplier_get_selector(company=user.company, uuid=uuid)
    SupplierService.delete(company=user.company, instance=supplier)
    return 204, None
