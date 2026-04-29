from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import ControllerBase, api_controller, route
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.dependencies import get_supplier
from apps.logistics.models.supplier import Supplier
from apps.logistics.schemas import SupplierIn, SupplierOut, SupplierPatchIn
from apps.logistics.services.supplier_service import SupplierService


@api_controller("/logistics/suppliers", tags=["Logistics"])
class SupplierController(ControllerBase):
    context: Any

    @route.get("/", response=list[SupplierOut], operation_id="logistics_suppliers_list")
    @paginate
    def list_suppliers(self) -> QuerySet[Supplier]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return SupplierService.list(user=self.context.request.user)

    @route.get(
        "/{supplier_uuid}/",
        response={200: SupplierOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_suppliers_read",
    )
    def retrieve_supplier(self, supplier_uuid: UUID4) -> Supplier:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_supplier(self.context.request, supplier_uuid)

    @route.post(
        "/",
        response={201: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_create",
    )
    def create_supplier(self, payload: SupplierIn) -> tuple[int, Supplier]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        supplier = SupplierService.create(
            user=self.context.request.user, data=payload.model_dump()
        )
        return 201, supplier

    @route.patch(
        "/{supplier_uuid}/",
        response={200: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_update",
    )
    def update_supplier(
        self, supplier_uuid: UUID4, payload: SupplierPatchIn
    ) -> Supplier:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        supplier = get_supplier(self.context.request, supplier_uuid)
        return SupplierService.update(
            instance=supplier, data=payload.model_dump(exclude_unset=True)
        )

    @route.delete(
        "/{supplier_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_delete",
    )
    def delete_supplier(self, supplier_uuid: UUID4) -> tuple[int, None]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        supplier = get_supplier(self.context.request, supplier_uuid)
        SupplierService.delete(instance=supplier)
        return 204, None
