import pytest
from django.core.exceptions import ValidationError

from apps.logistics.models import Supplier
from apps.logistics.tests.factories import SupplierFactory


@pytest.mark.django_db
class TestSupplierModelMetadata:
    """Testes de representação e metadados do modelo Supplier."""

    def test_supplier_str_is_name(self):
        """__str__ deve retornar o nome do fornecedor."""
        supplier = SupplierFactory.build(name="Buffet Master")
        assert str(supplier) == "Buffet Master"

    def test_supplier_ordering_by_name(self):
        """Ordenação padrão deve ser alfabética por name."""
        SupplierFactory.create(name="Zeta")
        SupplierFactory.create(name="Alfa")
        SupplierFactory.create(name="Beta")

        suppliers = list(Supplier.objects.all())
        assert suppliers[0].name == "Alfa"
        assert suppliers[1].name == "Beta"
        assert suppliers[2].name == "Zeta"

    def test_supplier_is_active_default(self):
        """is_active deve ser True por padrão."""
        supplier = SupplierFactory.build()
        assert supplier.is_active is True


@pytest.mark.django_db
class TestSupplierFullAddress:
    """Testes da computed property full_address."""

    def test_full_address_with_all_fields(self):
        """full_address deve concatenar address, city e state."""
        supplier = SupplierFactory.build(
            address="Rua das Flores, 123",
            city="São Paulo",
            state="SP",
        )

        result = supplier.full_address
        assert "Rua das Flores, 123" in result
        assert "São Paulo" in result
        assert "SP" in result

    def test_full_address_without_state(self):
        """full_address sem state não deve incluir campo vazio."""
        supplier = SupplierFactory.build(
            address="Av. Paulista, 1000",
            city="São Paulo",
            state="",
        )

        result = supplier.full_address
        assert result == "Av. Paulista, 1000, São Paulo"

    def test_full_address_minimal(self):
        """full_address com campos vazios deve retornar string enxuta."""
        supplier = SupplierFactory.build(
            address="",
            city="Rio de Janeiro",
            state="",
        )

        result = supplier.full_address
        assert "Rio de Janeiro" in result
        assert result.count(", ") == 0


@pytest.mark.django_db
class TestSupplierCnpjValidation:
    """Testes de validação do campo CNPJ via full_clean()."""

    def test_full_clean_rejects_invalid_cnpj(self):
        """full_clean() deve disparar ValidationError para CNPJ inválido."""
        supplier = SupplierFactory.build(cnpj="123")

        with pytest.raises(ValidationError) as exc_info:
            supplier.full_clean()
        assert "cnpj" in exc_info.value.message_dict

    def test_full_clean_accepts_valid_cnpj(self):
        """full_clean() deve aceitar CNPJ no formato correto."""
        supplier = SupplierFactory.create(
            cnpj="00.000.000/0001-00",
        )

        supplier.full_clean()

    def test_full_clean_accepts_empty_cnpj(self):
        """full_clean() deve aceitar CNPJ vazio (blank=True)."""
        supplier = SupplierFactory.create(
            cnpj="",
        )

        supplier.full_clean()
