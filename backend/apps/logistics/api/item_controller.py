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
from apps.logistics.models import Item
from apps.logistics.schemas import (
    ItemIn,
    ItemOut,
    ItemPatchIn,
)
from apps.logistics.services import ItemService


@api_controller("/logistics/items", tags=["Logistics"])
class ItemController(ControllerBase):
    def __init__(self, service: ItemService):
        self.service = service

    @http_get("/", response=list[ItemOut], operation_id="logistics_items_list")
    @paginate
    def list_items(self, wedding_id: UUID4 | None = None) -> QuerySet[Item]:
        """Lista itens/entregáveis do casamento."""
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/{uuid}/",
        response={200: ItemOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_items_read",
    )
    def retrieve_item(self, uuid: UUID4) -> Item:
        """Retorna detalhes de um item."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_create",
    )
    def create_item(self, payload: ItemIn) -> tuple[int, Item]:
        """Cria um novo item no logística."""
        item = self.service.create(self.context.request.user, payload.model_dump())
        return 201, item

    @http_patch(
        "/{uuid}/",
        response={200: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_partial_update",
    )
    def partial_update_item(self, uuid: UUID4, payload: ItemPatchIn) -> Item:
        """Atualiza parcialmente um item."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_delete",
    )
    def delete_item(self, uuid: UUID4) -> tuple[int, None]:
        """Remove um item."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
