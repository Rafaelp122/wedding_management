from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.logistics.models import Item
from apps.logistics.services.item_service import ItemService
from apps.logistics.tests.factories import ContractFactory, ItemFactory, SupplierFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_item_context(user):
    """Helper: cria wedding + contract no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    supplier = SupplierFactory(company=user.company)
    contract = ContractFactory(wedding=wedding, supplier=supplier)
    return wedding, contract


@pytest.mark.django_db
class TestItemServiceCreate:
    """Testes de criação de itens via ItemService."""

    def test_create_item_with_contract(self, user):
        """Criação de item vinculado a contrato — wedding deriva do contrato."""
        wedding, contract = _setup_item_context(user)

        data = {
            "contract": contract.uuid,
            "name": "Buquê de Rosas",
            "quantity": 5,
        }

        item = ItemService.create(user.company, data)

        assert item.contract == contract
        assert item.wedding == wedding
        assert item.name == "Buquê de Rosas"
        assert item.quantity == 5
        assert item.acquisition_status == Item.AcquisitionStatus.PENDING

    def test_create_item_with_explicit_wedding_no_contract(self, user):
        """Item pode ser criado sem contrato, com wedding explícito."""
        wedding, _ = _setup_item_context(user)

        data = {
            "wedding": wedding.uuid,
            "name": "Item avulso",
            "quantity": 1,
        }

        item = ItemService.create(user.company, data)

        assert item.wedding == wedding
        assert item.contract is None

    def test_create_item_with_contract_instance(self, user):
        """create() aceita instância de Contract."""
        _, contract = _setup_item_context(user)

        data = {
            "contract": contract,
            "name": "Cadeiras",
            "quantity": 100,
        }

        item = ItemService.create(user.company, data)
        assert item.contract == contract

    def test_create_item_contract_not_found(self, user):
        """UUID de contrato inexistente levanta ObjectNotFoundError."""
        data = {
            "contract": uuid4(),
            "name": "Fantasma",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user.company, data)

        assert "contract_not_found_or_denied" in str(exc_info.value.code)

    def test_create_item_multitenancy_contract(self):
        """Usuário A não pode criar item com contrato do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, contract_b = _setup_item_context(user_b)

        data = {
            "contract": contract_b.uuid,
            "name": "Invasão",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user_a.company, data)

        assert "contract_not_found_or_denied" in str(exc_info.value.code)

    def test_create_item_without_contract_and_wedding_raises_error(self, user):
        """
        Sem contrato E sem wedding, create() levanta BusinessRuleViolation
        em vez de IntegrityError obscuro do banco.
        """
        data = {
            "name": "Item solto no vácuo",
            "quantity": 1,
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ItemService.create(user.company, data)

        assert "item_missing_wedding" in str(exc_info.value.code)

    def test_create_item_mismatched_wedding_and_contract(self, user):
        """
        Se contract e wedding são fornecidos e divergem,
        levanta DomainIntegrityError.
        """
        _, contract_a = _setup_item_context(user)
        wedding_b = WeddingFactory(user_context=user)

        data = {
            "contract": contract_a.uuid,
            "wedding": wedding_b.uuid,
            "name": "Item conflitante",
            "quantity": 1,
        }

        with pytest.raises(DomainIntegrityError) as exc_info:
            ItemService.create(user.company, data)

        assert "item_contract_wedding_mismatch" in str(exc_info.value.code)

    def test_create_item_matching_wedding_and_contract(self, user):
        """
        Se contract e wedding são fornecidos e coincidem,
        cria o item com sucesso.
        """
        wedding, contract = _setup_item_context(user)

        data = {
            "contract": contract.uuid,
            "wedding": wedding.uuid,
            "name": "Item consistente",
            "quantity": 1,
        }

        item = ItemService.create(user.company, data)
        assert item.contract == contract
        assert item.wedding == wedding

    def test_create_item_with_wedding_instance(self, user):
        """Criação de item passando uma instância de Wedding diretamente."""
        wedding, _ = _setup_item_context(user)

        data = {
            "wedding": wedding,
            "name": "Item com instância",
            "quantity": 2,
        }

        item = ItemService.create(user.company, data)

        assert item.wedding == wedding
        assert item.contract is None
        assert item.name == "Item com instância"

    def test_create_item_with_invalid_wedding_type_raises_error(self, user):
        """Criação de item com tipo inválido de casamento levanta erro."""
        data = {
            "wedding": 12345,  # Tipo inválido (int)
            "name": "Item inválido",
            "quantity": 1,
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ItemService.create(user.company, data)

        assert "item_missing_wedding" in str(exc_info.value.code)

    def test_create_item_with_nonexistent_wedding_uuid_raises_error(self, user):
        """
        Criação de item com UUID de casamento inexistente
        levanta ObjectNotFoundError.
        """
        data = {
            "wedding": uuid4(),
            "name": "Item fantasma",
            "quantity": 1,
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ItemService.create(user.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestItemServiceUpdate:
    """Testes de atualização de itens via ItemService."""

    def test_update_item_name(self, user):
        """Atualização de campos simples é permitida."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding, name="Velho")

        updated = ItemService.update(user.company, item, {"name": "Novo Nome"})

        assert updated.name == "Novo Nome"

    def test_update_item_acquisition_status(self, user):
        """Troca de status de aquisição é permitida (BR-L04)."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        updated = ItemService.update(
            user.company,
            item,
            {"acquisition_status": Item.AcquisitionStatus.IN_PROGRESS},
        )

        assert updated.acquisition_status == Item.AcquisitionStatus.IN_PROGRESS

    def test_update_item_cannot_change_wedding(self, user):
        """Wedding é bloqueado no update."""
        wedding1, contract = _setup_item_context(user)
        wedding2 = WeddingFactory(user_context=user)
        item = ItemFactory(contract=contract, wedding=wedding1)

        updated = ItemService.update(user.company, item, {"wedding": wedding2.uuid})

        assert updated.wedding == wedding1

    def test_update_item_cannot_change_company(self, user):
        """Company é bloqueada no update."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)
        other_user = UserFactory()

        updated = ItemService.update(
            user.company, item, {"company": other_user.company}
        )

        assert updated.company == user.company

    def test_update_item_clear_contract(self, user):
        """Item pode ser desvinculado do contrato (contract=None)."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        updated = ItemService.update(user.company, item, {"contract": None})

        assert updated.contract is None

    def test_update_item_contract_matching_wedding(self, user):
        """Atualização do contrato para um contrato com casamento correspondente."""
        wedding, contract1 = _setup_item_context(user)
        supplier = SupplierFactory(company=user.company)
        contract2 = ContractFactory(wedding=wedding, supplier=supplier)
        item = ItemFactory(contract=contract1, wedding=wedding)

        updated = ItemService.update(user.company, item, {"contract": contract2})

        assert updated.contract == contract2

    def test_update_item_contract_mismatched_wedding_raises_error(self, user):
        """Atualização do contrato para um com casamento diferente levanta erro."""
        wedding1, contract1 = _setup_item_context(user)
        wedding2 = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract2 = ContractFactory(wedding=wedding2, supplier=supplier)
        item = ItemFactory(contract=contract1, wedding=wedding1)

        with pytest.raises(DomainIntegrityError) as exc_info:
            ItemService.update(user.company, item, {"contract": contract2})

        assert "item_contract_wedding_mismatch" in str(exc_info.value.code)


@pytest.mark.django_db
class TestItemServiceDelete:
    """Testes de deleção de itens via ItemService."""

    def test_delete_item_success(self, user):
        """Deleção de item sem dependências é permitida."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding)

        ItemService.delete(user.company, item)

        assert Item.objects.filter(uuid=item.uuid).count() == 0


@pytest.mark.django_db
class TestItemServiceListAndGet:
    """Testes de listagem e obtenção de itens."""

    def test_list_items_multitenancy(self):
        """list() retorna apenas itens do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a, contract_a = _setup_item_context(user_a)
        wedding_b, contract_b = _setup_item_context(user_b)

        ItemFactory(contract=contract_a, wedding=wedding_a, name="Item A")
        ItemFactory(contract=contract_b, wedding=wedding_b, name="Item B")

        qs_a = ItemService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().name == "Item A"

        qs_b = ItemService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().name == "Item B"

    def test_list_items_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        wedding1, contract = _setup_item_context(user)
        wedding2 = WeddingFactory(user_context=user)

        ItemFactory(contract=contract, wedding=wedding1, name="Item W1")
        ItemFactory(wedding=wedding2, name="Item W2")

        qs = ItemService.list(user.company, wedding_id=wedding1.uuid)
        assert qs.count() == 1
        assert qs.first().name == "Item W1"

    def test_get_item_success(self, user):
        """get() retorna item com select_related."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(contract=contract, wedding=wedding, name="Toalhas")

        result = ItemService.get(user.company, item.uuid)
        assert result.uuid == item.uuid
        assert result.name == "Toalhas"

    def test_get_item_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            ItemService.get(user.company, uuid4())

    def test_get_item_multitenancy(self):
        """Usuário A não pode acessar item do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        _, contract_b = _setup_item_context(user_b)
        item_b = ItemFactory(contract=contract_b, wedding=contract_b.wedding)

        with pytest.raises(ObjectNotFoundError):
            ItemService.get(user_a.company, item_b.uuid)


@pytest.mark.django_db
class TestItemServiceTransitionStatus:
    """Testes da máquina de estados de itens."""

    def test_pending_to_in_progress(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        result = ItemService.transition_status(user.company, item, "IN_PROGRESS")
        assert result.acquisition_status == "IN_PROGRESS"

    def test_in_progress_to_done(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="IN_PROGRESS"
        )
        result = ItemService.transition_status(user.company, item, "DONE")
        assert result.acquisition_status == "DONE"

    def test_in_progress_to_pending(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="IN_PROGRESS"
        )
        result = ItemService.transition_status(user.company, item, "PENDING")
        assert result.acquisition_status == "PENDING"

    def test_done_to_in_progress(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="DONE"
        )
        result = ItemService.transition_status(user.company, item, "IN_PROGRESS")
        assert result.acquisition_status == "IN_PROGRESS"

    def test_pending_to_done_invalid(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        with pytest.raises(BusinessRuleViolation):
            ItemService.transition_status(user.company, item, "DONE")

    def test_done_to_pending_invalid(self, user):
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="DONE"
        )
        with pytest.raises(BusinessRuleViolation):
            ItemService.transition_status(user.company, item, "PENDING")

    def test_transition_status_multitenancy(self, user):
        """Transição com company diferente deve falhar."""
        wedding, contract = _setup_item_context(user)
        item = ItemFactory(
            contract=contract, wedding=wedding, acquisition_status="PENDING"
        )
        other_user = UserFactory()

        with pytest.raises(ObjectNotFoundError):
            ItemService.transition_status(other_user.company, item, "IN_PROGRESS")
