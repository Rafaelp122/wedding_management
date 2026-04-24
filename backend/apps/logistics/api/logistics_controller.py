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
from apps.logistics.models import Contract, Item, Supplier
from apps.logistics.schemas import (
    ContractIn,
    ContractOut,
    ContractPatchIn,
    ItemIn,
    ItemOut,
    ItemPatchIn,
    SupplierIn,
    SupplierOut,
    SupplierPatchIn,
)
from apps.logistics.services import ContractService, ItemService, SupplierService


@api_controller("/logistics", tags=["Logistics"])
class LogisticsController(ControllerBase):
    """
    Controller para gestão logística.
    Centraliza fornecedores, contratos e itens em um único domínio.
    """

    def __init__(
        self,
        supplier_service: SupplierService,
        contract_service: ContractService,
        item_service: ItemService,
    ):
        self.supplier_service = supplier_service
        self.contract_service = contract_service
        self.item_service = item_service

    # --- Endpoints de Fornecedores ---

    @http_get(
        "/suppliers/",
        response=list[SupplierOut],
        operation_id="logistics_suppliers_list",
    )
    @paginate
    def list_suppliers(self) -> QuerySet[Supplier]:
        """Lista fornecedores do Planner logado."""
        return self.supplier_service.list(self.context.request.user)

    @http_get(
        "/suppliers/{uuid}/",
        response={200: SupplierOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_suppliers_read",
    )
    def retrieve_supplier(self, uuid: UUID4) -> Supplier:
        """Retorna detalhes de um fornecedor."""
        return self.supplier_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/suppliers/",
        response={201: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_create",
    )
    def create_supplier(self, payload: SupplierIn) -> tuple[int, Supplier]:
        """Cria um novo fornecedor."""
        supplier = self.supplier_service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, supplier

    @http_patch(
        "/suppliers/{uuid}/",
        response={200: SupplierOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_partial_update",
    )
    def partial_update_supplier(
        self, uuid: UUID4, payload: SupplierPatchIn
    ) -> Supplier:
        """Atualiza parcialmente um fornecedor."""
        return self.supplier_service.partial_update(
            self.context.request.user, uuid, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/suppliers/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_suppliers_delete",
    )
    def delete_supplier(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um fornecedor."""
        self.supplier_service.delete(self.context.request.user, uuid)
        return 204, None

    # --- Endpoints de Contratos ---

    @http_get(
        "/contracts/",
        response=list[ContractOut],
        operation_id="logistics_contracts_list",
    )
    @paginate
    def list_contracts(self, wedding_id: UUID4 | None = None) -> QuerySet[Contract]:
        """Lista contratos do Planner."""
        return self.contract_service.list(
            self.context.request.user, wedding_id=wedding_id
        )

    @http_get(
        "/contracts/{uuid}/",
        response={200: ContractOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_contracts_read",
    )
    def retrieve_contract(self, uuid: UUID4) -> Contract:
        """Retorna detalhes de um contrato."""
        return self.contract_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/contracts/",
        response={201: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_create",
    )
    def create_contract(self, payload: ContractIn) -> tuple[int, Contract]:
        """Cria um contrato vinculado a um orçamento."""
        contract = self.contract_service.create(
            self.context.request.user, payload.model_dump()
        )
        return 201, contract

    @http_patch(
        "/contracts/{uuid}/",
        response={200: ContractOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_partial_update",
    )
    def partial_update_contract(
        self, uuid: UUID4, payload: ContractPatchIn
    ) -> Contract:
        """Atualiza parcialmente um contrato."""
        return self.contract_service.partial_update(
            self.context.request.user, uuid, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/contracts/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_contracts_delete",
    )
    def delete_contract(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um contrato."""
        self.contract_service.delete(self.context.request.user, uuid)
        return 204, None

    # --- Endpoints de Itens ---

    @http_get("/items/", response=list[ItemOut], operation_id="logistics_items_list")
    @paginate
    def list_items(self, wedding_id: UUID4 | None = None) -> QuerySet[Item]:
        """Lista itens/entregáveis do casamento."""
        return self.item_service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/items/{uuid}/",
        response={200: ItemOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_items_read",
    )
    def retrieve_item(self, uuid: UUID4) -> Item:
        """Retorna detalhes de um item."""
        return self.item_service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/items/",
        response={201: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_create",
    )
    def create_item(self, payload: ItemIn) -> tuple[int, Item]:
        """Cria um novo item no logística."""
        item = self.item_service.create(self.context.request.user, payload.model_dump())
        return 201, item

    @http_patch(
        "/items/{uuid}/",
        response={200: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_partial_update",
    )
    def partial_update_item(self, uuid: UUID4, payload: ItemPatchIn) -> Item:
        """Atualiza parcialmente um item."""
        return self.item_service.partial_update(
            self.context.request.user, uuid, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/items/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_delete",
    )
    def delete_item(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um item."""
        self.item_service.delete(self.context.request.user, uuid)
        return 204, None
