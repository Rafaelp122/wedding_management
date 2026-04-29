import pytest

from apps.events.tests.factories import EventFactory
from apps.logistics.models import Item
from apps.logistics.tests.factories import ContractFactory, ItemFactory, SupplierFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestItemModel:
    """Testes de integridade do modelo Item."""

    def test_item_str(self):
        item = Item(name="Cadeira de Ferro", quantity=100)
        assert str(item) == "Cadeira de Ferro (100x)"

    def test_item_supplier_property(self, user):
        event = EventFactory(company=user.company)
        supplier = SupplierFactory(company=user.company, name="Locadora A")
        contract = ContractFactory(supplier=supplier, event=event)
        item = ItemFactory(contract=contract, event=event)

        assert item.supplier == supplier
