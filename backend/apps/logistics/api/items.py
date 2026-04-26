from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import ControllerBase, api_controller, route
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.core.dependencies import get_item
from apps.logistics.models.item import Item
from apps.logistics.schemas import ItemIn, ItemOut, ItemPatchIn
from apps.logistics.services.item_service import ItemService


@api_controller("/logistics/items", tags=["Logistics"])
class ItemController(ControllerBase):
    context: Any

    @route.get("/", response=list[ItemOut], operation_id="logistics_items_list")
    @paginate
    def list_items(self, wedding_id: UUID4 | None = None) -> QuerySet[Item]:
        return ItemService.list(user=self.context.request.user, wedding_id=wedding_id)

    @route.get(
        "/{item_uuid}/",
        response={200: ItemOut, **READ_ERROR_RESPONSES},
        operation_id="logistics_items_read",
    )
    def retrieve_item(self, item_uuid: UUID4) -> Item:
        return get_item(self.context.request, item_uuid)

    @route.post(
        "/",
        response={201: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_create",
    )
    def create_item(self, payload: ItemIn) -> tuple[int, Item]:
        item = ItemService.create(
            user=self.context.request.user, data=payload.model_dump()
        )
        return 201, item

    @route.patch(
        "/{item_uuid}/",
        response={200: ItemOut, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_update",
    )
    def update_item(self, item_uuid: UUID4, payload: ItemPatchIn) -> Item:
        item = get_item(self.context.request, item_uuid)
        return ItemService.update(
            user=self.context.request.user,
            instance=item,
            data=payload.model_dump(exclude_unset=True),
        )

    @route.delete(
        "/{item_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="logistics_items_delete",
    )
    def delete_item(self, item_uuid: UUID4) -> tuple[int, None]:
        item = get_item(self.context.request, item_uuid)
        ItemService.delete(instance=item)
        return 204, None
