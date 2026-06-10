from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
)
from apps.logistics.models import Contract
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory, ItemFactory, SupplierFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_contract_context(user):
    """Helper: cria wedding + supplier no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    supplier = SupplierFactory(company=user.company)
    return wedding, supplier


@pytest.mark.django_db
class TestContractServiceCreate:
    """Testes de criação de contratos via ContractService."""

    def test_create_contract_success(self, user):
        """Criação de contrato com wedding e supplier."""
        wedding, supplier = _setup_contract_context(user)

        data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Buffet Completo",
            "total_amount": Decimal("10000.00"),
            "description": "Buffet completo",
        }

        contract = ContractService.create(user.company, data)

        assert contract.wedding == wedding
        assert contract.supplier == supplier
        assert contract.total_amount == Decimal("10000.00")
        assert contract.status == Contract.StatusChoices.DRAFT

    def test_create_contract_with_instances(self, user):
        """create() aceita instâncias de Wedding e Supplier."""
        wedding, supplier = _setup_contract_context(user)

        data = {
            "wedding": wedding,
            "supplier": supplier,
            "name": "Buffet Teste",
            "total_amount": Decimal("5000.00"),
        }

        contract = ContractService.create(user.company, data)
        assert contract.wedding == wedding
        assert contract.supplier == supplier

    def test_create_contract_wedding_not_found(self, user):
        """UUID de wedding inexistente levanta ObjectNotFoundError."""
        _, supplier = _setup_contract_context(user)

        data = {
            "wedding": uuid4(),
            "supplier": supplier.uuid,
            "total_amount": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ContractService.create(user.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    def test_create_contract_supplier_not_found(self, user):
        """UUID de supplier inexistente levanta ObjectNotFoundError."""
        wedding, _ = _setup_contract_context(user)

        data = {
            "wedding": wedding.uuid,
            "supplier": uuid4(),
            "total_amount": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ContractService.create(user.company, data)

        assert "supplier_not_found_or_denied" in str(exc_info.value.code)

    def test_create_contract_multitenancy_wedding(self):
        """Usuário A não pode criar contrato com wedding do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        supplier_a = SupplierFactory(company=user_a.company)

        data = {
            "wedding": wedding_b.uuid,
            "supplier": supplier_a.uuid,
            "total_amount": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ContractService.create(user_a.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestContractServiceUpdate:
    """Testes de atualização de contratos via ContractService."""

    def test_update_contract_description(self, user):
        """Atualização de campos simples é permitida."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(
            wedding=wedding, supplier=supplier, description="Velha"
        )

        updated = ContractService.update(
            user.company, contract, {"description": "Nova descrição"}
        )

        assert updated.description == "Nova descrição"

    def test_update_contract_cannot_change_wedding(self, user):
        """Wedding é bloqueado no update (campo estrutural)."""
        wedding1, supplier = _setup_contract_context(user)
        wedding2 = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding1, supplier=supplier)

        updated = ContractService.update(
            user.company, contract, {"wedding": wedding2.uuid}
        )

        assert updated.wedding == wedding1

    def test_update_contract_change_supplier(self, user):
        """Troca de supplier é permitida com validação multitenant."""
        wedding, supplier1 = _setup_contract_context(user)
        supplier2 = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=wedding, supplier=supplier1)

        updated = ContractService.update(
            user.company, contract, {"supplier": supplier2.uuid}
        )

        assert updated.supplier == supplier2

    def test_update_with_valid_status_transition(self, make_contract):
        """update() com status válido chama transition_status internamente."""
        contract = make_contract("DRAFT")

        updated = ContractService.update(
            contract.company, contract, {"status": "PENDING"}
        )

        assert updated.status == "PENDING"

    def test_update_with_invalid_status_transition_raises_error(self, make_contract):
        """update() com transição inválida propaga BusinessRuleViolation."""
        contract = make_contract("DRAFT")

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.update(contract.company, contract, {"status": "SIGNED"})

        assert "Não é permitido transitar" in str(exc_info.value)


@pytest.mark.django_db
class TestContractServiceDelete:
    """Testes de deleção de contratos via ContractService."""

    def test_delete_contract_orphans_items(self, user):
        """Deleção de contrato desvincula itens (contract=None) antes de deletar."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        item = ItemFactory(contract=contract, wedding=wedding)

        ContractService.delete(user.company, contract)

        # Contrato foi deletado
        assert Contract.objects.filter(uuid=contract.uuid).count() == 0
        # Item sobreviveu, mas ficou órfão
        item.refresh_from_db()
        assert item.contract is None

    def test_delete_contract_with_expenses_succeeds(self, user):
        """Contrato com Expense vinculada pode ser deletado (SET_NULL).
        Diferente de amarras de integridade pesada, o vínculo Contrato-Despesa
        é flexível: deletar o contrato apenas deixa a despesa sem referência,
        preservando o rastro financeiro (parcelas)."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        ExpenseFactory(
            wedding=wedding,
            category=category,
            contract=contract,
            actual_amount=contract.total_amount,
        )

        ContractService.delete(user.company, contract)

        assert Contract.objects.filter(uuid=contract.uuid).count() == 0


@pytest.mark.django_db
class TestContractServiceListAndGet:
    """Testes de listagem e obtenção de contratos."""

    def test_list_contracts_multitenancy(self):
        """list() retorna apenas contratos do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)
        supplier_a = SupplierFactory(company=user_a.company)
        supplier_b = SupplierFactory(company=user_b.company)

        ContractFactory(
            wedding=wedding_a, supplier=supplier_a, description="Contrato A"
        )
        ContractFactory(
            wedding=wedding_b, supplier=supplier_b, description="Contrato B"
        )

        qs_a = ContractService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().description == "Contrato A"

        qs_b = ContractService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().description == "Contrato B"

    def test_list_contracts_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        wedding1, supplier = _setup_contract_context(user)
        wedding2 = WeddingFactory(user_context=user)

        ContractFactory(wedding=wedding1, supplier=supplier, description="C1")
        ContractFactory(wedding=wedding2, supplier=supplier, description="C2")

        qs = ContractService.list(user.company, wedding_id=wedding1.uuid)
        assert qs.count() == 1
        assert qs.first().description == "C1"

    def test_get_contract_success(self, user):
        """get() retorna contrato com select_related."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        result = ContractService.get(user.company, contract.uuid)
        assert result.uuid == contract.uuid
        assert result.supplier == supplier
        assert result.wedding == wedding

    def test_get_contract_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            ContractService.get(user.company, uuid4())

    def test_get_contract_multitenancy(self):
        """Usuário A não pode acessar contrato do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        supplier_b = SupplierFactory(company=user_b.company)
        contract_b = ContractFactory(wedding=wedding_b, supplier=supplier_b)

        with pytest.raises(ObjectNotFoundError):
            ContractService.get(user_a.company, contract_b.uuid)


@pytest.mark.django_db
class TestContractServiceUploadFile:
    """Testes de upload de arquivo para contrato via ContractService."""

    def test_upload_file_invalid_content_type_fails(self, user):
        """upload_file com content_type inválido deve falhar (fast-fail)."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        invalid_file = SimpleUploadedFile(
            name="malicious.exe",
            content=b"malicious content",
            content_type="application/octet-stream",
        )

        with pytest.raises(ValidationError) as exc_info:
            ContractService.upload_file(user.company, contract.uuid, invalid_file)

        assert "não suportado" in str(exc_info.value).lower()

    def test_upload_file_exceeds_size_fails(self, user):
        """upload_file com arquivo > 10MB deve falhar (fast-fail)."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        oversized_file = SimpleUploadedFile(
            name="big_contract.pdf",
            content=b"0" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )

        with pytest.raises(ValidationError) as exc_info:
            ContractService.upload_file(user.company, contract.uuid, oversized_file)

        assert "10mb" in str(exc_info.value).lower()

    def test_upload_file_valid_pdf_succeeds(self, user):
        """upload_file com pdf válido deve salvar com sucesso."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        valid_file = SimpleUploadedFile(
            name="valid_contract.pdf",
            content=b"valid pdf content",
            content_type="application/pdf",
        )

        result = ContractService.upload_file(user.company, contract.uuid, valid_file)

        assert result.pdf_file.name.endswith(".pdf")
        assert result.uuid == contract.uuid


@pytest.mark.django_db
class TestContractServiceTransitionStatus:
    """Testes da máquina de estados de contratos."""

    def test_draft_to_pending(self, make_contract):
        contract = make_contract("DRAFT")
        result = ContractService.transition_status(
            contract.company, contract, "PENDING"
        )
        assert result.status == "PENDING"

    def test_draft_to_canceled(self, make_contract):
        contract = make_contract("DRAFT")
        result = ContractService.transition_status(
            contract.company, contract, "CANCELED"
        )
        assert result.status == "CANCELED"

    def test_pending_to_signed(self, make_contract):
        contract = make_contract("PENDING")
        contract.pdf_file = SimpleUploadedFile(
            "test.pdf", b"pdf content", content_type="application/pdf"
        )
        contract.signed_date = date.today()
        contract.total_amount = Decimal("5000.00")
        contract.save()
        result = ContractService.transition_status(contract.company, contract, "SIGNED")
        assert result.status == "SIGNED"

    def test_pending_to_draft(self, make_contract):
        contract = make_contract("PENDING")
        result = ContractService.transition_status(contract.company, contract, "DRAFT")
        assert result.status == "DRAFT"

    def test_pending_to_canceled(self, make_contract):
        contract = make_contract("PENDING")
        result = ContractService.transition_status(
            contract.company, contract, "CANCELED"
        )
        assert result.status == "CANCELED"

    def test_signed_to_canceled(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        result = ContractService.transition_status(
            contract.company, contract, "CANCELED"
        )
        assert result.status == "CANCELED"

    def test_canceled_to_draft(self, make_contract):
        contract = make_contract("CANCELED")
        result = ContractService.transition_status(contract.company, contract, "DRAFT")
        assert result.status == "DRAFT"

    def test_invalid_transition_raises_error(self, make_contract):
        contract = make_contract("DRAFT")
        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.transition_status(contract.company, contract, "SIGNED")
        assert "Não é permitido transitar" in str(exc_info.value)

    def test_signed_to_draft_invalid(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        with pytest.raises(BusinessRuleViolation):
            ContractService.transition_status(contract.company, contract, "DRAFT")

    def test_canceled_to_signed_invalid(self, make_contract):
        contract = make_contract("CANCELED")
        with pytest.raises(BusinessRuleViolation):
            ContractService.transition_status(contract.company, contract, "SIGNED")

    def test_transition_status_multitenancy(self, make_contract):
        """Transição com company diferente deve falhar — ou o service
        deve validar que instance pertence à company passada."""
        contract = make_contract("DRAFT")
        other_user = UserFactory()

        with pytest.raises(ObjectNotFoundError):
            ContractService.transition_status(other_user.company, contract, "PENDING")


@pytest.mark.django_db
class TestContractServiceDeleteFile:
    """Testes de remoção de arquivo de contrato."""

    def test_delete_file_success(self, contract_with_file):
        assert contract_with_file.pdf_file.name

        ContractService.delete_file(contract_with_file.company, contract_with_file.uuid)

        contract_with_file.refresh_from_db()
        assert contract_with_file.pdf_file.name == ""

    def test_delete_file_contract_not_found(self, user):
        with pytest.raises(ObjectNotFoundError):
            ContractService.delete_file(user.company, uuid4())

    def test_delete_file_multitenancy(self, contract_with_file, user):
        other_user = UserFactory()
        with pytest.raises(ObjectNotFoundError):
            ContractService.delete_file(other_user.company, contract_with_file.uuid)


@pytest.mark.django_db
class TestContractServiceResolveParent:
    """Testes de vinculação de contrato pai via update()."""

    def test_update_parent_success(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        parent = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        child = ContractFactory(wedding=wedding, supplier=supplier, status="DRAFT")
        ContractService.update(child.company, child, {"parent": str(parent.uuid)})

        child.refresh_from_db()
        assert child.parent == parent

    def test_update_parent_self_raises_error(self, make_contract):
        contract = make_contract("DRAFT")
        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.update(
                contract.company, contract, {"parent": str(contract.uuid)}
            )
        assert "não pode ser pai de si mesmo" in str(exc_info.value)

    def test_update_parent_cross_wedding_raises_error(self, user):
        parent = ContractFactory(
            wedding__company=user.company,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        child_wedding = WeddingFactory(company=user.company)
        child_supplier = SupplierFactory(company=user.company)
        child = ContractFactory(
            wedding=child_wedding, supplier=child_supplier, status="DRAFT"
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.update(child.company, child, {"parent": str(parent.uuid)})
        assert "deve pertencer ao mesmo casamento" in str(exc_info.value)

    def test_update_parent_circular_raises_error(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        ancestor = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        intermediate = ContractFactory(
            wedding=ancestor.wedding,
            supplier=ancestor.supplier,
            parent=ancestor,
            status="DRAFT",
        )
        child = ContractFactory(
            wedding=ancestor.wedding,
            supplier=ancestor.supplier,
            parent=intermediate,
            status="DRAFT",
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.update(
                ancestor.company, ancestor, {"parent": str(child.uuid)}
            )
        assert "descendente" in str(exc_info.value)

    def test_update_parent_not_found_raises_error(self, make_contract):
        contract = make_contract("DRAFT")
        with pytest.raises(ObjectNotFoundError):
            ContractService.update(contract.company, contract, {"parent": str(uuid4())})
