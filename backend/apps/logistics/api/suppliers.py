from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.models.supplier import Supplier
from apps.logistics.schemas import SupplierIn, SupplierOut, SupplierPatchIn
from apps.logistics.services.supplier_service import SupplierService


suppliers_router = Router(tags=["Logistics"])


@suppliers_router.get(
    "/", response=list[SupplierOut], operation_id="logistics_suppliers_list"
)
@paginate
def list_suppliers(request: HttpRequest) -> QuerySet[Supplier]:
    """
    Lista todos os fornecedores cadastrados pelo Planner logado.
    """
    return SupplierService.list(user=request.user)


@suppliers_router.get(
    "/{uuid:uuid}/",
    response={200: SupplierOut, **READ_ERROR_RESPONSES},
    operation_id="logistics_suppliers_read",
)
def retrieve_supplier(request: HttpRequest, uuid: UUID4) -> Supplier:
    """
    Retorna os detalhes de um fornecedor específico.
    """
    return SupplierService.get(user=request.user, uuid=uuid)


@suppliers_router.post(
    "/",
    response={201: SupplierOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_suppliers_create",
)
def create_supplier(request: HttpRequest, payload: SupplierIn) -> tuple[int, Supplier]:
    """
    Cadastra um novo fornecedor no sistema.
    """
    supplier = SupplierService.create(user=request.user, data=payload.model_dump())
    return 201, supplier


@suppliers_router.patch(
    "/{uuid:uuid}/",
    response={200: SupplierOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_suppliers_partial_update",
)
def partial_update_supplier(
    request: HttpRequest, uuid: UUID4, payload: SupplierPatchIn
) -> Supplier:
    """
    Atualiza informações específicas de um fornecedor (nome, contato, categorias).
    """
    supplier = SupplierService.get(user=request.user, uuid=uuid)
    data = payload.model_dump(exclude_unset=True)
    return SupplierService.partial_update(
        user=request.user, instance=supplier, data=data
    )


@suppliers_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_suppliers_delete",
)
def delete_supplier(request: HttpRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove o cadastro de um fornecedor do sistema.
    """
    supplier = SupplierService.get(user=request.user, uuid=uuid)
    SupplierService.delete(user=request.user, instance=supplier)
    return 204, None
