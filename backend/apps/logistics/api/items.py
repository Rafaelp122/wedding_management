from django.db.models import QuerySet
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.logistics.models.item import Item
from apps.logistics.schemas import ItemIn, ItemOut, ItemPatchIn
from apps.logistics.services.item_service import ItemService
from apps.users.auth import require_user
from apps.users.types import AuthRequest


items_router = Router(tags=["Logistics"])


@items_router.get("/", response=list[ItemOut], operation_id="logistics_items_list")
@paginate
def list_items(request: AuthRequest, wedding_id: UUID4 | None = None) -> QuerySet[Item]:
    """
    Lista os itens e materiais logísticos gerados nas tabelas de aprovação.
    Permite filtrar por casamento.
    """
    user = require_user(request.user)
    return ItemService.list(company=user.company, wedding_id=wedding_id)


@items_router.get(
    "/{uuid:uuid}/",
    response={200: ItemOut, **READ_ERROR_RESPONSES},
    operation_id="logistics_items_read",
)
def retrieve_item(request: AuthRequest, uuid: UUID4) -> Item:
    """
    Mostra os detalhes nominais de um item logístico específico.
    """
    user = require_user(request.user)
    return ItemService.get(company=user.company, uuid=uuid)


@items_router.post(
    "/",
    response={201: ItemOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_items_create",
)
def create_item(request: AuthRequest, payload: ItemIn) -> tuple[int, Item]:
    """
    Adiciona um recurso físico no painel de acompanhamento.
    Parte do planejamento logístico de um evento.
    """
    user = require_user(request.user)
    item = ItemService.create(company=user.company, data=payload.model_dump())
    return 201, item


@items_router.patch(
    "/{uuid:uuid}/",
    response={200: ItemOut, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_items_update",
)
def update_item(request: AuthRequest, uuid: UUID4, payload: ItemPatchIn) -> Item:
    """
    Atualiza quantidades ou informações de apoio do lote do item em questão.
    """
    user = require_user(request.user)
    item = ItemService.get(company=user.company, uuid=uuid)
    data = payload.model_dump(exclude_unset=True)
    return ItemService.update(company=user.company, instance=item, data=data)


@items_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="logistics_items_delete",
)
def delete_item(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Exclui permanentemente o indicativo do item.
    Remove das listas logísticas rastreadas pelo Planner.
    """
    user = require_user(request.user)
    item = ItemService.get(company=user.company, uuid=uuid)
    ItemService.delete(company=user.company, instance=item)
    return 204, None
