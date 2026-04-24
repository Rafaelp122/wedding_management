from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.models import Supplier
from apps.logistics.schemas import (
    SupplierIn,
    SupplierOut,
    SupplierPatchIn,
)
from apps.logistics.services import SupplierService


@api_controller("/logistics/suppliers", tags=["Logistics"])
class SupplierController(ControllerBase):
    def __init__(self, service: SupplierService):
        self.service = service

    @http_get("/", response=list[SupplierOut], operation_id="logistics_suppliers_list")
    @paginate
    def list_suppliers(self) -> QuerySet[Supplier]:
        """Lista fornecedores do Planner logado."""
        return self.service.list(self.context.request.user)

    @http_get(
        "/{uuid}/",
        response={200: SupplierOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_suppliers_read",
    )
    def retrieve_supplier(self, uuid: UUID4) -> Supplier:
        """Retorna detalhes de um fornecedor."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_create",
    )
    def create_supplier(self, payload: SupplierIn) -> tuple[int, Supplier]:
        """Cria um novo fornecedor."""
        supplier = self.service.create(self.context.request.user, payload.model_dump())
        return 201, supplier

    @http_patch(
        "/{uuid}/",
        response={200: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_partial_update",
    )
    def partial_update_supplier(
        self, uuid: UUID4, payload: SupplierPatchIn
    ) -> Supplier:
        """Atualiza parcialmente um fornecedor."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_delete",
    )
    def delete_supplier(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um fornecedor."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
