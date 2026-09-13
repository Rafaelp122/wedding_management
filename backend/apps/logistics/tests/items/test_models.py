from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError

from apps.core.exceptions import BusinessRuleViolation
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
class TestItemQuantityValidation:
    """Testes da regra invariante de quantidade mínima do item (clean)."""

    def test_item_quantity_zero_raises_validation_error(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        item = Item(wedding=wedding, company=user.company, name="Flores", quantity=0)
        with pytest.raises(ValidationError) as exc_info:
            item.clean()
        assert "quantity" in exc_info.value.message_dict
        assert "no mínimo 1 unidade" in str(exc_info.value.message_dict["quantity"])

    def test_item_quantity_positive_passes_clean(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        item = Item(wedding=wedding, company=user.company, name="Flores", quantity=1)
        item.clean()


@pytest.mark.django_db
class TestItemStatusTransitionValidation:
    """Testes da máquina de estados e métodos de ciclo de vida do modelo Item."""

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
    def test_can_transition_to_valid(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        assert item.can_transition_to(to_status) is True

    @pytest.mark.parametrize("from_status, to_status", _INVALID)
    def test_can_transition_to_invalid(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        assert item.can_transition_to(to_status) is False

    def test_can_transition_to_same_status_is_true(
        self, item_for_transition: Any
    ) -> None:
        item = item_for_transition("PENDING")
        assert item.can_transition_to("PENDING") is True
        assert item.can_transition_to(Item.AcquisitionStatus.PENDING) is True

    @pytest.mark.parametrize("from_status, to_status", _VALID)
    def test_transition_to_valid(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        item.transition_to(to_status)
        assert item.acquisition_status == to_status

    @pytest.mark.parametrize("from_status, to_status", _INVALID)
    def test_transition_to_invalid_raises_violation(
        self, item_for_transition: Any, from_status: str, to_status: str
    ) -> None:
        item = item_for_transition(from_status)
        with pytest.raises(BusinessRuleViolation) as exc_info:
            item.transition_to(to_status)
        msg = f"Não é permitido transitar de '{from_status}' para '{to_status}'"
        assert msg in str(exc_info.value.detail)

    def test_transition_to_same_status_noop(self, item_for_transition: Any) -> None:
        item = item_for_transition("PENDING")
        item.transition_to("PENDING")
        assert item.acquisition_status == "PENDING"

    def test_semantic_start(self, item_for_transition: Any) -> None:
        item = item_for_transition("PENDING")
        item.start()
        assert item.acquisition_status == Item.AcquisitionStatus.IN_PROGRESS
        assert item.is_in_progress is True

    def test_semantic_complete(self, item_for_transition: Any) -> None:
        item = item_for_transition("IN_PROGRESS")
        item.complete()
        assert item.acquisition_status == Item.AcquisitionStatus.DONE
        assert item.is_done is True

    def test_semantic_reopen(self, item_for_transition: Any) -> None:
        item = item_for_transition("DONE")
        item.reopen()
        assert item.acquisition_status == Item.AcquisitionStatus.IN_PROGRESS
        assert item.is_in_progress is True

    def test_semantic_revert_to_pending(self, item_for_transition: Any) -> None:
        item = item_for_transition("IN_PROGRESS")
        item.revert_to_pending()
        assert item.acquisition_status == Item.AcquisitionStatus.PENDING
        assert item.is_pending is True

    def test_convenience_properties(self, item_for_transition: Any) -> None:
        item = item_for_transition("PENDING")
        assert item.is_pending is True
        assert item.is_in_progress is False
        assert item.is_done is False
