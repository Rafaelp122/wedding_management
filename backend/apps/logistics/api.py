from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

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
from apps.logistics.services.contract_service import ContractService
from apps.logistics.services.item_service import ItemService
from apps.logistics.services.supplier_service import SupplierService


# Routers isolados por conceito, garantindo autenticação em todas rotas da API
suppliers_router = Router(tags=["Logistics"])
contracts_router = Router(tags=["Logistics"])
items_router = Router(tags=["Logistics"])


# ==============================================================================
# SUPPLIERS
# ==============================================================================
@suppliers_router.get(
    "/", response=list[SupplierOut], operation_id="logistics_suppliers_list"
)
@paginate
def list_suppliers(request):
    """
    Lista todos os fornecedores cadastrados pelo Planner logado.
    """
    return SupplierService.list(user=request.user)


@suppliers_router.get(
    "/{uuid:uuid}/", response=SupplierOut, operation_id="logistics_suppliers_read"
)
def retrieve_supplier(request, uuid: UUID4):
    """
    Retorna os detalhes de um fornecedor específico.
    """
    return SupplierService.get(user=request.user, uuid=uuid)


@suppliers_router.post(
    "/", response={201: SupplierOut}, operation_id="logistics_suppliers_create"
)
def create_supplier(request, payload: SupplierIn):
    """
    Cadastra um novo fornecedor no sistema.
    """
    supplier = SupplierService.create(user=request.user, data=payload.model_dump())
    return 201, supplier


@suppliers_router.patch(
    "/{uuid:uuid}/",
    response=SupplierOut,
    operation_id="logistics_suppliers_partial_update",
)
def partial_update_supplier(request, uuid: UUID4, payload: SupplierPatchIn):
    """
    Atualiza informações específicas de um fornecedor (nome, contato, categorias).
    """
    supplier = SupplierService.get(user=request.user, uuid=uuid)
    # Exclude unset parameters to just update what frontend sends
    data = payload.model_dump(exclude_unset=True)
    return SupplierService.partial_update(
        user=request.user, instance=supplier, data=data
    )


@suppliers_router.delete(
    "/{uuid:uuid}/", response={204: None}, operation_id="logistics_suppliers_delete"
)
def delete_supplier(request, uuid: UUID4):
    """
    Remove o cadastro de um fornecedor do sistema.
    """
    supplier = SupplierService.get(user=request.user, uuid=uuid)
    SupplierService.delete(user=request.user, instance=supplier)
    return 204, None


# ==============================================================================
# CONTRACTS
# ==============================================================================
@contracts_router.get(
    "/", response=list[ContractOut], operation_id="logistics_contracts_list"
)
@paginate
def list_contracts(request):
    """
    Lista os contratos de fornecedores associados aos casamentos do Planner.
    """
    return ContractService.list(user=request.user)


@contracts_router.get(
    "/{uuid:uuid}/", response=ContractOut, operation_id="logistics_contracts_read"
)
def retrieve_contract(request, uuid: UUID4):
    """
    Exibe as cláusulas e informações completas de um contrato.
    """
    return ContractService.get(user=request.user, uuid=uuid)


@contracts_router.post(
    "/", response={201: ContractOut}, operation_id="logistics_contracts_create"
)
def create_contract(request, payload: ContractIn):
    """
    Associa um fornecedor a um casamento através de um novo contrato logístico.
    """
    contract = ContractService.create(user=request.user, data=payload.model_dump())
    return 201, contract


@contracts_router.patch(
    "/{uuid:uuid}/",
    response=ContractOut,
    operation_id="logistics_contracts_partial_update",
)
def partial_update_contract(request, uuid: UUID4, payload: ContractPatchIn):
    """
    Altera o status, valores agregados ou observações de um contrato existente na base.
    """
    contract = ContractService.get(user=request.user, uuid=uuid)
    data = payload.model_dump(exclude_unset=True)
    return ContractService.partial_update(
        user=request.user, instance=contract, data=data
    )


@contracts_router.delete(
    "/{uuid:uuid}/", response={204: None}, operation_id="logistics_contracts_delete"
)
def delete_contract(request, uuid: UUID4):
    """
    Deleta o contrato e rompe o vínculo entre o fornecedor e a organização do evento.
    """
    contract = ContractService.get(user=request.user, uuid=uuid)
    ContractService.delete(user=request.user, instance=contract)
    return 204, None


# ==============================================================================
# ITEMS
# ==============================================================================
@items_router.get("/", response=list[ItemOut], operation_id="logistics_items_list")
@paginate
def list_items(request):
    """
    Lista os itens e materiais logísticos gerados nas tabelas de aprovação.
    """
    return ItemService.list(user=request.user)


@items_router.get(
    "/{uuid:uuid}/", response=ItemOut, operation_id="logistics_items_read"
)
def retrieve_item(request, uuid: UUID4):
    """
    Mostra os detalhes nominais de um item logístico específico.
    """
    return ItemService.get(user=request.user, uuid=uuid)


@items_router.post("/", response={201: ItemOut}, operation_id="logistics_items_create")
def create_item(request, payload: ItemIn):
    """
    Adiciona um recurso físico no painel de acompanhamento.
    Parte do planejamento logístico de um evento.
    """
    item = ItemService.create(user=request.user, data=payload.model_dump())
    return 201, item


@items_router.patch(
    "/{uuid:uuid}/", response=ItemOut, operation_id="logistics_items_partial_update"
)
def partial_update_item(request, uuid: UUID4, payload: ItemPatchIn):
    """
    Atualiza quantidades ou informações de apoio do lote do item em questão.
    """
    item = ItemService.get(user=request.user, uuid=uuid)
    data = payload.model_dump(exclude_unset=True)
    return ItemService.partial_update(user=request.user, instance=item, data=data)


@items_router.delete(
    "/{uuid:uuid}/", response={204: None}, operation_id="logistics_items_delete"
)
def delete_item(request, uuid: UUID4):
    """
    Exclui permanentemente o indicativo do item.
    Remove das listas logísticas rastreadas pelo Planner.
    """
    item = ItemService.get(user=request.user, uuid=uuid)
    ItemService.delete(user=request.user, instance=item)
    return 204, None
