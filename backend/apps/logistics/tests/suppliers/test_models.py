import pytest
from django.core.exceptions import ValidationError

from apps.logistics.models import Supplier
from apps.logistics.tests.factories import SupplierFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestSupplierModel:
    """Testes de integridade do modelo Supplier."""

    def test_supplier_str(self):
        supplier = Supplier(name="Banda Show")
        assert str(supplier) == "Banda Show"

    def test_full_address_formatting(self):
        supplier = Supplier(address="Rua A, 10", city="São Paulo", state="SP")
        assert supplier.full_address == "Rua A, 10, São Paulo, SP"

    def test_name_max_length(self, user):
        supplier = SupplierFactory.build(planner=user, name="A" * 256)
        with pytest.raises(ValidationError):
            supplier.full_clean()
