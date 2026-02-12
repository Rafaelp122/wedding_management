from django.db import transaction

from apps.logistics.dto import ItemDTO
from apps.logistics.models import Item


class ItemService:
    @staticmethod
    @transaction.atomic
    def create(dto: ItemDTO) -> Item:
        """Cria o item garantindo a integridade transacional."""
        item = Item.objects.create(
            wedding_id=dto.wedding_id,
            contract_id=dto.contract_id,
            budget_category_id=dto.budget_category_id,
            name=dto.name,
            description=dto.description,
            quantity=dto.quantity,
            acquisition_status=dto.acquisition_status,
        )
        return item

    @staticmethod
    @transaction.atomic
    def update(instance: Item, dto: ItemDTO) -> Item:
        """Atualiza o item e dispara a validação clean()."""
        instance.contract_id = dto.contract_id
        instance.budget_category_id = dto.budget_category_id
        instance.name = dto.name
        instance.description = dto.description
        instance.quantity = dto.quantity
        instance.acquisition_status = dto.acquisition_status

        instance.save()  # Dispara full_clean() -> Valida RF07.1
        return instance
