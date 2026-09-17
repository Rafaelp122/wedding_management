import pytest
from django.core.exceptions import ValidationError

from apps.logistics.models import Supplier
from apps.logistics.tests.factories import SupplierFactory


@pytest.mark.django_db
class TestSupplierModelMetadata:
    """Testes de representação e metadados do modelo Supplier."""

    def test_supplier_str_is_name(self) -> None:
        """__str__ deve retornar o nome do fornecedor."""
        supplier = SupplierFactory.build(name="Buffet Master")
        assert str(supplier) == "Buffet Master"

    def test_supplier_ordering_by_name(self) -> None:
        """Ordenação padrão deve ser alfabética por name."""
        SupplierFactory.create(name="Zeta")
        SupplierFactory.create(name="Alfa")
        SupplierFactory.create(name="Beta")

        suppliers = list(Supplier.objects.all())
        assert suppliers[0].name == "Alfa"
        assert suppliers[1].name == "Beta"
        assert suppliers[2].name == "Zeta"

    def test_supplier_is_active_default(self) -> None:
        """is_active deve ser True por padrão."""
        supplier = SupplierFactory.build()
        assert supplier.is_active is True


@pytest.mark.django_db
class TestSupplierCnpjValidation:
    """Testes de validação do campo CNPJ via full_clean()."""

    def test_full_clean_rejects_invalid_cnpj(self) -> None:
        """full_clean() deve disparar ValidationError para CNPJ inválido."""
        supplier = SupplierFactory.build(cnpj="123")

        with pytest.raises(ValidationError) as exc_info:
            supplier.full_clean()
        assert "cnpj" in exc_info.value.message_dict

    def test_full_clean_accepts_valid_cnpj(self) -> None:
        """full_clean() deve aceitar CNPJ no formato correto."""
        supplier = SupplierFactory.create(
            cnpj="00.000.000/0001-00",
        )

        supplier.full_clean()

    def test_full_clean_accepts_empty_cnpj(self) -> None:
        """full_clean() deve aceitar CNPJ vazio (blank=True)."""
        supplier = SupplierFactory.create(
            cnpj="",
        )

        supplier.full_clean()


@pytest.mark.django_db
class TestSupplierActivation:
    """Testes de ativação e desativação semântica de fornecedor."""

    def test_deactivate_supplier(self) -> None:
        supplier = SupplierFactory.create(is_active=True)
        supplier.deactivate()
        assert supplier.is_active is False

    def test_activate_supplier(self) -> None:
        supplier = SupplierFactory.create(is_active=False)
        supplier.activate()
        assert supplier.is_active is True
