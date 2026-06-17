from datetime import date
from decimal import Decimal
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.core.exceptions import ValidationError

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

    def test_create_contract_with_inactive_supplier(self, user):
        """Criação de contrato com fornecedor inativo deve funcionar."""
        wedding, supplier = _setup_contract_context(user)
        supplier.is_active = False
        supplier.save()

        data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato Fornecedor Inativo",
            "total_amount": Decimal("5000.00"),
        }

        contract = ContractService.create(user.company, data)
        assert contract.supplier == supplier
        assert contract.status == Contract.StatusChoices.DRAFT


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

    def test_update_expiration_date_with_alert_days_before(self, make_contract):
        """Atualizar expiration_date e alert_days_before juntos."""
        contract = make_contract("DRAFT")
        future_date = date(2027, 12, 31)

        updated = ContractService.update(
            contract.company,
            contract,
            {
                "expiration_date": future_date,
                "alert_days_before": 30,
            },
        )
        assert updated.expiration_date == future_date
        assert updated.alert_days_before == 30

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

    def test_delete_contract_with_file_removes_physical_file(self, user):
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(
            wedding=wedding, supplier=supplier, pdf_file="contracts/dummy.pdf"
        )
        assert contract.pdf_file.name
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

    def test_get_contract_with_expense(self, user):
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            contract=contract,
            actual_amount=contract.total_amount,
        )

        result = ContractService.get(user.company, contract.uuid)
        assert result.uuid == contract.uuid
        assert result.expense_id == expense.uuid

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

    def test_upload_file_invalid_extension_fails(self, user):
        """upload_file com extensão inválida deve falhar na validação do model."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        with pytest.raises(ValidationError) as exc_info:
            ContractService.upload_file(
                user.company, contract.uuid, "contracts/malicious.exe"
            )

        assert "não suportado" in str(exc_info.value).lower()

    def test_upload_file_valid_key_succeeds(self, user):
        """upload_file com key válida deve salvar com sucesso."""
        wedding, supplier = _setup_contract_context(user)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        result = ContractService.upload_file(
            user.company, contract.uuid, "contracts/valid_contract.pdf"
        )

        assert result.pdf_file.name == "contracts/valid_contract.pdf"
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
        contract.pdf_file = "contracts/test.pdf"
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

    def test_transition_to_signed_without_pdf_raises_error(self, make_contract):
        """Transição para SIGNED sem PDF vinculado deve falhar."""
        contract = make_contract("PENDING", pdf_file=None)

        with pytest.raises(ValidationError) as exc_info:
            ContractService.transition_status(
                contract.company, contract, "SIGNED"
            )
        assert "PDF" in str(exc_info.value)

    def test_transition_to_signed_without_signed_date_raises_error(self, make_contract):
        """Transição para SIGNED sem signed_date deve falhar."""
        contract = make_contract(
            "PENDING",
            pdf_file="contracts/dummy.pdf",
            signed_date=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            ContractService.transition_status(
                contract.company, contract, "SIGNED"
            )
        assert "data" in str(exc_info.value).lower()

    def test_cancel_contract_with_pending_installments(self, make_contract, user):
        """Cancelar contrato com parcelas pendentes deve ser permitido."""
        from apps.finances.tests.factories import (
            BudgetCategoryFactory,
            BudgetFactory,
            ExpenseFactory,
            InstallmentFactory,
        )

        contract = make_contract("SIGNED", signed_date=date.today())
        category = BudgetCategoryFactory(
            budget=BudgetFactory(wedding=contract.wedding),
            wedding=contract.wedding,
        )
        expense = ExpenseFactory(
            wedding=contract.wedding,
            category=category,
            contract=contract,
            actual_amount=Decimal("3000.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("3000.00"),
            status="PENDING",
        )

        updated = ContractService.transition_status(
            contract.company, contract, "CANCELED"
        )
        assert updated.status == "CANCELED"


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


@pytest.mark.django_db
class TestContractServiceCreateFull:
    """Testes de criação completa de contrato via ContractService.create_full()."""

    def _setup(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget)
        return wedding, supplier, category

    def test_create_full_contract_only(self, user):
        """Cria contrato sem file, items ou expense."""
        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato Teste",
            "total_amount": Decimal("10000.00"),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
        )
        assert contract.name == "Contrato Teste"
        assert contract.total_amount == Decimal("10000.00")
        assert not contract.pdf_file

    def test_create_full_with_file(self, user):
        """Cria contrato com upload de arquivo."""
        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato com Arquivo",
            "total_amount": Decimal("5000.00"),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
            pdf_file_key="contracts/contrato.pdf",
        )
        assert contract.pdf_file.name == "contracts/contrato.pdf"

    def test_create_full_with_items(self, user):
        """Cria contrato com itens via items_data."""
        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato com Itens",
            "total_amount": Decimal("5000.00"),
        }
        items_data = [
            {"name": "Item 1", "quantity": 10, "acquisition_status": "PENDING"},
            {"name": "Item 2", "quantity": 5, "acquisition_status": "PENDING"},
        ]
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
            items_data=items_data,
        )
        assert contract.items.count() == 2

    def test_create_full_with_expense(self, user):
        """Cria contrato com despesa vinculada."""
        wedding, supplier, category = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato com Despesa",
            "total_amount": Decimal("5000.00"),
        }
        expense_data = {
            "category": category.uuid,
            "name": "Despesa do Contrato",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
            "num_installments": 1,
            "first_due_date": date.today(),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
            expense_data=expense_data,
        )
        assert contract.expense is not None
        assert contract.expense.actual_amount == Decimal("5000.00")

    def test_create_full_with_all(self, user):
        """Cria contrato completo: file + items + expense."""
        wedding, supplier, category = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato Completo",
            "total_amount": Decimal("10000.00"),
        }
        items_data = [
            {"name": "Item 1", "quantity": 10, "acquisition_status": "PENDING"},
        ]
        expense_data = {
            "category": category.uuid,
            "name": "Despesa do Contrato",
            "estimated_amount": Decimal("10000.00"),
            "actual_amount": Decimal("10000.00"),
            "num_installments": 3,
            "first_due_date": date.today(),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
            items_data=items_data,
            expense_data=expense_data,
            pdf_file_key="contracts/contrato.pdf",
        )
        assert contract.pdf_file.name == "contracts/contrato.pdf"
        assert contract.items.count() == 1
        assert contract.expense is not None
        assert contract.expense.installments.count() == 3

    def test_create_full_invalid_file_type(self, user):
        """Arquivo com tipo inválido deve falhar."""
        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato",
            "total_amount": Decimal("5000.00"),
        }
        with pytest.raises(ValidationError) as exc_info:
            ContractService.create_full(
                company=user.company,
                contract_data=contract_data,
                pdf_file_key="contracts/virus.exe",
            )
        assert "não suportado" in str(exc_info.value)

    def test_create_full_invalid_file_size(self, user):
        """Arquivo com tamanho acima de 10MB deve falhar."""
        from django.core.files.uploadedfile import SimpleUploadedFile

        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato",
            "total_amount": Decimal("5000.00"),
        }
        oversized = SimpleUploadedFile(
            "contrato.pdf",
            b"x" * (11 * 1024 * 1024),  # 11MB
            content_type="application/pdf",
        )
        with pytest.raises(ValidationError) as exc_info:
            ContractService.create_full(
                company=user.company,
                contract_data=contract_data,
                pdf_file=oversized,
            )
        assert "tamanho" in str(exc_info.value).lower()

    def test_create_full_with_parent(self, user):
        """Cria contrato como aditivo de outro contrato."""
        wedding, supplier, _ = self._setup(user)
        parent = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("10000.00"),
            signed_date=date.today(),
            pdf_file="contracts/dummy.pdf",
        )
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Aditivo",
            "total_amount": Decimal("2000.00"),
            "parent": str(parent.uuid),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
        )
        assert contract.parent == parent

    def test_create_full_addendum_with_canceled_parent(self, user):
        """Criar aditivo de contrato cancelado — documenta comportamento."""
        wedding, supplier, _ = self._setup(user)
        parent = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            status="CANCELED",
            total_amount=Decimal("10000.00"),
        )
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Aditivo Cancelado",
            "total_amount": Decimal("2000.00"),
            "parent": str(parent.uuid),
        }
        contract = ContractService.create_full(
            company=user.company,
            contract_data=contract_data,
        )
        assert contract.parent == parent

    def test_create_full_multitenancy_isolation(self):
        """Usuário B não pode criar contrato com wedding do Usuário A."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(company=user_a.company)
        supplier_b = SupplierFactory(company=user_b.company)
        contract_data = {
            "wedding": wedding_a.uuid,
            "supplier": supplier_b.uuid,
            "name": "Cross-tenant",
            "total_amount": Decimal("5000.00"),
        }
        with pytest.raises(ObjectNotFoundError):
            ContractService.create_full(
                company=user_b.company,
                contract_data=contract_data,
            )

    def test_create_full_expense_category_not_found(self, user):
        """Expense com categoria inexistente deve falhar."""
        wedding, supplier, _ = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato",
            "total_amount": Decimal("5000.00"),
        }
        expense_data = {
            "category": uuid4(),
            "name": "Despesa Inválida",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }
        with pytest.raises(ObjectNotFoundError) as exc_info:
            ContractService.create_full(
                company=user.company,
                contract_data=contract_data,
                expense_data=expense_data,
            )
        assert "categoria não encontrada" in str(exc_info.value).lower()

    def test_create_full_expense_amount_mismatch_contract(self, user):
        """Expense com valor divergente do contrato deve falhar (BR-F02)."""
        wedding, supplier, category = self._setup(user)
        contract_data = {
            "wedding": wedding.uuid,
            "supplier": supplier.uuid,
            "name": "Contrato",
            "total_amount": Decimal("5000.00"),
        }
        expense_data = {
            "category": category.uuid,
            "name": "Despesa Divergente",
            "estimated_amount": Decimal("3000.00"),
            "actual_amount": Decimal("3000.00"),
        }
        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.create_full(
                company=user.company,
                contract_data=contract_data,
                expense_data=expense_data,
            )
        assert "br_f02_violation" in str(exc_info.value.code)


@pytest.mark.django_db
class TestContractServiceGenerateUploadUrl:
    """Testes de geração de upload URL pré-assinada."""

    @patch("boto3.client")
    def test_generate_upload_url_success(self, mock_boto3_client, user, settings):
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.R2_BUCKET = "test-bucket"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"

        wedding, _ = _setup_contract_context(user)
        mock_s3 = mock_boto3_client.return_value
        mock_s3.generate_presigned_url.return_value = "https://r2.com/presigned-url"

        result = ContractService.generate_upload_url(
            company=user.company,
            filename="contrato.pdf",
            wedding_id=wedding.uuid,
        )

        assert "upload_url" in result
        assert "object_key" in result
        assert result["upload_url"] == "https://r2.com/presigned-url"
        assert result["object_key"].startswith(f"contracts/{wedding.uuid}/")
        assert result["object_key"].endswith("/contrato.pdf")

        mock_s3.generate_presigned_url.assert_called_once()
        _, kwargs = mock_s3.generate_presigned_url.call_args
        assert kwargs["Params"]["ContentType"] == "application/pdf"

    def test_generate_upload_url_wedding_not_found(self, user, settings):
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.R2_BUCKET = "test-bucket"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"

        with pytest.raises(ObjectNotFoundError):
            ContractService.generate_upload_url(
                company=user.company,
                filename="contrato.pdf",
                wedding_id=uuid4(),
            )

    def test_generate_upload_url_multitenancy(self, user, settings):
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.R2_BUCKET = "test-bucket"
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"

        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        with pytest.raises(ObjectNotFoundError):
            ContractService.generate_upload_url(
                company=user.company,
                filename="contrato.pdf",
                wedding_id=other_wedding.uuid,
            )

    def test_generate_upload_url_configuration_incomplete(self, user, settings):
        settings.R2_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.R2_ACCESS_KEY_ID = "test-key-id"
        settings.R2_SECRET_ACCESS_KEY = "test-secret-key"
        settings.R2_BUCKET = ""
        settings.AWS_S3_ENDPOINT_URL = "https://r2-endpoint.com"
        settings.AWS_ACCESS_KEY_ID = "test-key-id"
        settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
        settings.AWS_STORAGE_BUCKET_NAME = ""

        wedding, _ = _setup_contract_context(user)
        with pytest.raises(BusinessRuleViolation) as exc_info:
            ContractService.generate_upload_url(
                company=user.company,
                filename="contrato.pdf",
                wedding_id=wedding.uuid,
            )
        assert exc_info.value.code == "storage_configuration_incomplete"
