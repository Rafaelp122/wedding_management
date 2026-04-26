import pytest

from apps.logistics.models import Item
from apps.logistics.tests.factories import ContractFactory, ItemFactory, SupplierFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestItemModel:
    """Testes de integridade do modelo Item."""

    def test_item_str(self):
        item = Item(name="Cadeira de Ferro", quantity=100)
        assert str(item) == "Cadeira de Ferro (100x)"

    def test_item_supplier_property(self, user):
        wedding = WeddingFactory(planner=user)
        supplier = SupplierFactory(planner=user, name="Locadora A")
        contract = ContractFactory(supplier=supplier, wedding=wedding)
        item = ItemFactory(contract=contract, wedding=wedding)

        assert item.supplier == supplier
