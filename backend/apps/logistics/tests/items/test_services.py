from typing import Any, cast, no_type_check
from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.logistics.models import Contract, Item, Supplier
from apps.logistics.schemas import ItemIn, ItemPatchIn
from apps.logistics.services.item_service import ItemService
from apps.logistics.tests.factories import ContractFactory as _ContractFactory
from apps.logistics.tests.factories import ItemFactory as _ItemFactory
from apps.logistics.tests.factories import SupplierFactory as _SupplierFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ItemFactory(*args: Any, **kwargs: Any) -> Item:
    return cast(Item, _ItemFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def _setup_item_context(user: User) -> tuple[Wedding, Contract]:
    """Helper: cria wedding + contract no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    supplier = SupplierFactory(company=user.company)
    contract = ContractFactory(wedding=wedding, supplier=supplier)
    return wedding, contract


@pytest.mark.django_db
class TestItemServiceCreate:
    """Testes de criação de itens via ItemService."""

    def test_create_item_with_contract(self, user: Any) -> None:
        """Criação de item vinculado a contrato — wedding deriva do contrato."""
        wedding, contract = _setup_item_context(user)

        data: dict[str, Any] = {
            "contract": contract.uuid,
            "name": "Buquê de Rosas",
            "quantity": 5,
        }

        item = ItemService.create(user.company, ItemIn(**data))

        assert item.contract == contract
        assert item.wedding == wedding
        assert item.name == "Buquê de Rosas"
        assert item.quantity == 5
        assert item.acquisition_status == Item.AcquisitionStatus.PENDING

    def test_create_item_with_explicit_wedding_no_contract(self, user: Any) -> None:
        """Item pode ser criado sem contrato, com wedding explícito."""
        wedding, _ = _setup_item_context(user)

        data: dict[str, Any] = {
            "wedding": wedding.uuid,
            "name": "Item avulso",
            "quantity": 1,
        }

        item = ItemService.create(user.company, ItemIn(**data))

        assert item.wedding == wedding
        assert item.contract is None

    def test_create_item_with_contract_instance(self, user: Any) -> None:
        """create() aceita instância de Contract."""
        _, contract = _setup_item_context(user)

        data: dict[str, Any] = {
            "contract": contract.uuid,
            "name": "Cadeiras",
            "quantity": 100,
        }

        item = ItemService.create(user.company, ItemIn(**data))
        assert item.contract == contract

    def test_create_item_contract_not_found(self, user: Any) -> None:
        """UUID de contrato inexistente levanta ObjectNotFoundError."""
        data: dict[str, Any] = {
            "contract": uuid4(),
            "name": "Fantasma",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user.company, ItemIn(**data))

        assert "contract_not_found_or_denied" in str(exc_info.value.code)

    def test_create_item_multitenancy_contract(self) -> None:
        """Usuário A não pode criar item com contrato do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, contract_b = _setup_item_context(user_b)

        data: dict[str, Any] = {
            "contract": contract_b.uuid,
            "name": "Invasão",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user_a.company, ItemIn(**data))

        assert "contract_not_found_or_denied" in str(exc_info.value.code)

    @no_type_check
    def test_create_item_rejects_contract_instance_from_other_tenant(self) -> None:
        """Instância de Contract pré-carregada também passa por validação tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, contract_b = _setup_item_context(user_b)
        payload = ItemIn.model_construct(
            wedding=None,
            contract=contract_b,
            name="Invasão por instância",
            description="",
            quantity=1,
            acquisition_status="PENDING",
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user_a.company, payload)

        assert exc_info.value.code == "contract_not_found_or_denied"

    def test_create_item_without_contract_and_wedding_raises_error(
        self, user: Any
    ) -> None:
        """
        Sem contrato E sem wedding, create() levanta BusinessRuleViolation
        em vez de IntegrityError obscuro do banco.
        """
        data: dict[str, Any] = {
            "name": "Item solto no vácuo",
            "quantity": 1,
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ItemService.create(user.company, ItemIn(**data))

        assert "item_missing_wedding" in str(exc_info.value.code)

    def test_create_item_mismatched_wedding_and_contract(self, user: Any) -> None:
        """
        Se contract e wedding são fornecidos e divergem,
        levanta DomainIntegrityError.
        """
        _, contract_a = _setup_item_context(user)
        wedding_b = WeddingFactory(user_context=user)

        data: dict[str, Any] = {
            "contract": contract_a.uuid,
            "wedding": wedding_b.uuid,
            "name": "Item conflitante",
            "quantity": 1,
        }

        with pytest.raises(DomainIntegrityError) as exc_info:
            ItemService.create(user.company, ItemIn(**data))

        assert "item_contract_wedding_mismatch" in str(exc_info.value.code)

    def test_create_item_matching_wedding_and_contract(self, user: Any) -> None:
        """
        Se contract e wedding são fornecidos e coincidem,
        cria o item com sucesso.
        """
        wedding, contract = _setup_item_context(user)

        data: dict[str, Any] = {
            "contract": contract.uuid,
            "wedding": wedding.uuid,
            "name": "Item consistente",
            "quantity": 1,
        }

        item = ItemService.create(user.company, ItemIn(**data))
        assert item.contract == contract
        assert item.wedding == wedding

    def test_create_item_with_wedding_instance(self, user: Any) -> None:
        """Criação de item passando uma instância de Wedding diretamente."""
        wedding, _ = _setup_item_context(user)

        data: dict[str, Any] = {
            "wedding": wedding.uuid,
            "name": "Item com instância",
            "quantity": 1,
        }

        item = ItemService.create(user.company, ItemIn(**data))
        assert item.wedding == wedding

    def test_create_item_with_nonexistent_wedding_uuid_raises_error(
        self, user: Any
    ) -> None:
        """
        Criação de item com UUID de casamento inexistente
        levanta ObjectNotFoundError.
        """
        data: dict[str, Any] = {
            "wedding": uuid4(),
            "name": "Item fantasma",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user.company, ItemIn(**data))

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestItemServiceUpdate:
    """Testes de atualização de itens via ItemService."""

    def test_update_item_name(self, user: Any) -> None:
        """Atualização de campos simples é permitida."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding, name="Velho")

        updated = ItemService.update(
            user.company, item, ItemPatchIn.model_construct(name="Novo Nome")
        )

        assert updated.name == "Novo Nome"

    def test_update_item_acquisition_status(self, user: Any) -> None:
        """Troca de status de aquisição é permitida (BR-L04)."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        updated = ItemService.update(
            user.company,
            item,
            ItemPatchIn.model_construct(
                acquisition_status=Item.AcquisitionStatus.IN_PROGRESS
            ),
        )

        assert updated.acquisition_status == Item.AcquisitionStatus.IN_PROGRESS

    def test_update_item_cannot_change_wedding(self, user: Any) -> None:
        """Wedding é bloqueado no update."""
        wedding1, contract = _setup_item_context(user)
        wedding2 = WeddingFactory(user_context=user)
        item = ItemFactory(contract=contract, wedding=wedding1)

        updated = ItemService.update(
            user.company, item, ItemPatchIn.model_construct(wedding=wedding2.uuid)
        )

        assert updated.wedding == wedding1

    def test_update_item_cross_tenant(self, user: Any) -> None:
        """Item de outro tenant não pode ser atualizado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_supplier = SupplierFactory(company=other_user.company)
        other_contract = ContractFactory(wedding=other_wedding, supplier=other_supplier)
        other_item = ItemFactory(contract=other_contract, wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            ItemService.update(
                user.company,
                other_item,
                ItemPatchIn.model_construct(name="Hack"),
            )

    def test_update_item_clear_contract(self, user: Any) -> None:
        """Item pode ser desvinculado do contrato (contract=None)."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        updated = ItemService.update(
            user.company, item, ItemPatchIn.model_construct(contract=None)
        )

        assert updated.contract is None

    def test_update_item_contract_matching_wedding(self, user: Any) -> None:
        """Atualização do contrato para um contrato com casamento correspondente."""
        wedding, contract1 = _setup_item_context(user)
        supplier = SupplierFactory(company=user.company)
        contract2 = ContractFactory(wedding=wedding, supplier=supplier)
        item = ItemFactory(contract=contract1, wedding=wedding)

        updated = ItemService.update(
            user.company,
            item,
            ItemPatchIn.model_construct(contract=contract2.uuid),
        )

        assert updated.contract == contract2

    def test_update_item_contract_mismatched_wedding_raises_error(
        self, user: Any
    ) -> None:
        """Atualização do contrato para um com casamento diferente levanta erro."""
        wedding1, contract1 = _setup_item_context(user)
        wedding2 = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract2 = ContractFactory(wedding=wedding2, supplier=supplier)
        item = ItemFactory(contract=contract1, wedding=wedding1)

        with pytest.raises(DomainIntegrityError) as exc_info:
            ItemService.update(
                user.company,
                item,
                ItemPatchIn.model_construct(contract=contract2.uuid),
            )

        assert "item_contract_wedding_mismatch" in str(exc_info.value.code)


@pytest.mark.django_db
class TestItemServiceDelete:
    """Testes de deleção de itens via ItemService."""

    def test_delete_item_success(self, user: Any) -> None:
        """Deleção de item sem dependências é permitida."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        ItemService.delete(user.company, item)

        assert Item.objects.filter(uuid=item.uuid).count() == 0

    def test_delete_item_cross_tenant(self, user: Any) -> None:
        """Item de outro tenant não pode ser deletado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_supplier = SupplierFactory(company=other_user.company)
        other_contract = ContractFactory(wedding=other_wedding, supplier=other_supplier)
        other_item = ItemFactory(contract=other_contract, wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            ItemService.delete(user.company, instance=other_item)


@pytest.mark.django_db
class TestItemServiceTransitionStatus:
    """Testes da máquina de estados de itens."""

    def test_pending_to_in_progress(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        result = ItemService.transition_status(user.company, item, "IN_PROGRESS")
        assert result.acquisition_status == "IN_PROGRESS"

    def test_in_progress_to_done(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="IN_PROGRESS"
        )
        result = ItemService.transition_status(user.company, item, "DONE")
        assert result.acquisition_status == "DONE"

    def test_in_progress_to_pending(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="IN_PROGRESS"
        )
        result = ItemService.transition_status(user.company, item, "PENDING")
        assert result.acquisition_status == "PENDING"

    def test_done_to_in_progress(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="DONE"
        )
        result = ItemService.transition_status(user.company, item, "IN_PROGRESS")
        assert result.acquisition_status == "IN_PROGRESS"

    def test_pending_to_done_invalid(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        with pytest.raises(BusinessRuleViolation):
            ItemService.transition_status(user.company, item, "DONE")

    def test_done_to_pending_invalid(self, user: Any) -> None:
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="DONE"
        )
        with pytest.raises(BusinessRuleViolation):
            ItemService.transition_status(user.company, item, "PENDING")

    def test_transition_status_multitenancy(self, user: Any) -> None:
        """Transição com company diferente deve falhar."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        other_user = UserFactory()

        with pytest.raises(ObjectNotFoundError):
            ItemService.transition_status(other_user.company, item, "IN_PROGRESS")
