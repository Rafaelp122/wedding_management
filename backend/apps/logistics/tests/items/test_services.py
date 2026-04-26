from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.logistics.models import Item
from apps.logistics.services.item_service import ItemService
from apps.logistics.tests.factories import ItemFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestItemService:
    """Testes de lógica de negócio para ItemService - Foco em Cobertura."""

    def test_list_items_with_filter(self, user):
        wedding = WeddingFactory(planner=user)
        ItemFactory(wedding=wedding)
        # Outro wedding do mesmo planner
        other_wedding = WeddingFactory(planner=user)
        ItemFactory(wedding=other_wedding)

        qs = ItemService.list(user, wedding_id=wedding.uuid)
        assert qs.count() == 1

    def test_get_item_logic(self, user):
        item = ItemFactory(wedding__planner=user)

        # Caso 1: Sucesso
        fetched = ItemService.get(user, item.uuid)
        assert fetched.id == item.id

        # Caso 2: Não encontrado
        from uuid import uuid4

        with pytest.raises(ObjectNotFoundError):
            ItemService.get(user, uuid4())

    def test_delete_item_protected_error(self, user):
        item = ItemFactory(wedding__planner=user)

        with pytest.raises(DomainIntegrityError):
            with patch.object(Item, "delete", side_effect=ProtectedError("Erro", [])):
                ItemService.delete(item)
