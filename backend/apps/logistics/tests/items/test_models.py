from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError

from apps.logistics.models import Contract, Item
from apps.logistics.tests.factories import ContractFactory as _ContractFactory
from apps.logistics.tests.factories import ItemFactory as _ItemFactory
from apps.users.models import User
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ItemFactory(*args: Any, **kwargs: Any) -> Item:
    return cast(Item, _ItemFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestItemModelMetadata:
    """Testes de representação e metadados do modelo Item."""

    def test_item_str_contains_name_and_quantity(self, user: Any) -> None:
        """__str__ deve conter nome e quantidade."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding)
        item = ItemFactory(
            contract=contract, wedding=wedding, name="Buquê de Rosas", quantity=5
        )

        result = str(item)
        assert "Buquê de Rosas" in result
        assert "5x" in result

    def test_item_ordering_by_created_at_descending(self, user: Any) -> None:
        """Ordenação padrão deve ser por -created_at."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding)
        i1 = ItemFactory(contract=contract, wedding=wedding, name="Primeiro")
        i2 = ItemFactory(contract=contract, wedding=wedding, name="Segundo")

        items = list(Item.objects.all())
        assert items[0] == i2
        assert items[1] == i1

    def test_item_acquisition_status_default_pending(self, user: Any) -> None:
        """Status de aquisição padrão deve ser PENDING."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(wedding=wedding)
        assert item.acquisition_status == Item.AcquisitionStatus.PENDING

    def test_item_quantity_default_one(self, user: Any) -> None:
        """Quantidade padrão do modelo deve ser 1 (usando build para isolar factory)."""
        wedding = WeddingFactory(user_context=user)
        item = Item(wedding=wedding, name="Teste")
        assert item.quantity == 1


@pytest.mark.django_db
class TestItemSupplierProperty:
    """Testes da computed property supplier."""

    def test_item_supplier_comes_from_contract(self, user: Any) -> None:
        """Fornecedor do item é derivado do contrato associado."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, supplier__name="Decorações Ltda")
        item = ItemFactory(contract=contract, wedding=wedding)

        assert item.supplier is not None
        assert item.supplier.name == "Decorações Ltda"

    def test_item_supplier_none_when_no_contract(self, user: Any) -> None:
        """Item sem contrato retorna supplier=None."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(wedding=wedding, contract=None)
        assert item.supplier is None


@pytest.mark.django_db
class TestItemAcquisitionStatus:
    """
    Testes das transições de status de aquisição
    (BR-L04: independente de pagamento).
    """

    def test_item_can_be_pending(self, user: Any) -> None:
        """Item criado como PENDING é válido."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(
            wedding=wedding, acquisition_status=Item.AcquisitionStatus.PENDING
        )
        item.full_clean()

    def test_item_can_be_in_progress(self, user: Any) -> None:
        """Item pode transitar para IN_PROGRESS."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(
            wedding=wedding, acquisition_status=Item.AcquisitionStatus.IN_PROGRESS
        )
        item.full_clean()

    def test_item_can_be_done(self, user: Any) -> None:
        """Item pode transitar para DONE."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(
            wedding=wedding, acquisition_status=Item.AcquisitionStatus.DONE
        )
        item.full_clean()


@pytest.mark.django_db
class TestItemStatusTransitionValidation:
    """Testes da máquina de estados de item em Item.clean()."""

    _VALID: list[tuple[str, str]] = [
        ("PENDING", "IN_PROGRESS"),
        ("IN_PROGRESS", "DONE"),
        ("IN_PROGRESS", "PENDING"),
        ("DONE", "IN_PROGRESS"),
    ]

    _INVALID: list[tuple[str, str]] = [
        ("PENDING", "DONE"),
        ("DONE", "PENDING"),
    ]

    @pytest.fixture
    def item_for_transition(self, user: User) -> Any:
        wedding = WeddingFactory(user_context=user)
        return lambda status: ItemFactory(wedding=wedding, acquisition_status=status)

    @pytest.mark.parametrize("from_status, to_status", _VALID)
    def test_valid_transitions(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        item.acquisition_status = to_status
        item.full_clean()

    @pytest.mark.parametrize("from_status, to_status", _INVALID)
    def test_invalid_transitions(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        item.acquisition_status = to_status
        with pytest.raises(ValidationError):
            item.full_clean()

    def test_no_change_does_not_validate(self, item_for_transition: Any) -> None:
        item = item_for_transition("PENDING")
        item.acquisition_status = "PENDING"
        item.full_clean()
