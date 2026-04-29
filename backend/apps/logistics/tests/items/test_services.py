from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.events.tests.factories import EventFactory
from apps.logistics.models import Item
from apps.logistics.services.item_service import ItemService
from apps.logistics.tests.factories import ItemFactory


@pytest.mark.django_db
@pytest.mark.service
class TestItemService:
    """Testes de lógica de negócio para ItemService - Foco em Cobertura."""

    def test_list_items_with_filter(self, user):
        event = EventFactory(company=user.company)
        ItemFactory(event=event)
        # Outro event do mesmo planner
        other_event = EventFactory(company=user.company)
        ItemFactory(event=other_event)

        qs = ItemService.list(user, event_id=event.uuid)
        assert qs.count() == 1

    def test_get_item_logic(self, user):
        event = EventFactory(company=user.company)
        item = ItemFactory(event=event)

        # Caso 1: Sucesso
        fetched = ItemService.get(user, item.uuid)
        assert fetched.id == item.id

        # Caso 2: Não encontrado
        from uuid import uuid4

        with pytest.raises(ObjectNotFoundError):
            ItemService.get(user, uuid4())

    def test_delete_item_protected_error(self, user):
        event = EventFactory(company=user.company)
        item = ItemFactory(event=event)

        with pytest.raises(DomainIntegrityError):
            with patch.object(Item, "delete", side_effect=ProtectedError("Erro", [])):
                ItemService.delete(item)
