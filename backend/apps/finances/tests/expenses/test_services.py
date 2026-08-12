from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import Any, cast, no_type_check
from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import (
    Budget,
    BudgetCategory,
    Expense,
    Installment,
)
from apps.finances.schemas import ExpenseIn, ExpensePatchIn
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import BudgetFactory as _BudgetFactory
from apps.finances.tests.factories import ExpenseFactory as _ExpenseFactory
from apps.finances.tests.factories import InstallmentFactory as _InstallmentFactory
from apps.logistics.models import Contract, Supplier
from apps.logistics.tests.factories import ContractFactory as _ContractFactory
from apps.logistics.tests.factories import SupplierFactory as _SupplierFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def BudgetCategoryFactory(*args: Any, **kwargs: Any) -> BudgetCategory:
    return cast(BudgetCategory, _BudgetCategoryFactory(*args, **kwargs))


def BudgetFactory(*args: Any, **kwargs: Any) -> Budget:
    return cast(Budget, _BudgetFactory(*args, **kwargs))


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ExpenseFactory(*args: Any, **kwargs: Any) -> Expense:
    return cast(Expense, _ExpenseFactory(*args, **kwargs))


def InstallmentFactory(*args: Any, **kwargs: Any) -> Installment:
    return cast(Installment, _InstallmentFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def _setup_category(user: User) -> BudgetCategory:
    """Helper: cria wedding + budget + category no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    return category


@pytest.mark.django_db
class TestExpenseServiceCreate:
    """Testes de criação de despesas via ExpenseService."""

    def test_create_expense_success(self, user: Any) -> None:
        """Criação de despesa válida com categoria."""
        category = _setup_category(user)

        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Buffet Premium",
            "description": "Buffet completo",
            "estimated_amount": Decimal("10000.00"),
            "actual_amount": Decimal("10000.00"),
        }

        expense = ExpenseService.create(user.company, ExpenseIn(**data))

        assert expense.category == category
        assert expense.wedding == category.wedding
        assert expense.name == "Buffet Premium"
        assert expense.actual_amount == Decimal("10000.00")

    def test_create_expense_with_category_instance(self, user: Any) -> None:
        """create() aceita instância de BudgetCategory, não só UUID."""
        category = _setup_category(user)

        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Fotografia",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        expense = ExpenseService.create(user.company, ExpenseIn(**data))
        assert expense.category == category

    def test_create_expense_inherits_wedding_from_category(self, user: Any) -> None:
        """Expense.wedding é injetado a partir da categoria."""
        category = _setup_category(user)

        expense = ExpenseService.create(
            user.company,
            ExpenseIn(
                category=category.uuid,
                name="Decoração",
                estimated_amount=Decimal("3000.00"),
                actual_amount=Decimal("3000.00"),
                num_installments=None,
            ),
        )

        assert expense.wedding == category.wedding

    def test_create_expense_category_not_found(self, user: Any) -> None:
        """UUID de categoria inexistente levanta ObjectNotFoundError."""
        data: dict[str, Any] = {
            "category": uuid4(),
            "name": "Fantasminha",
            "estimated_amount": Decimal("100.00"),
            "actual_amount": Decimal("100.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.create(user.company, ExpenseIn(**data))

        assert "budget_category_not_found_or_denied" in str(exc_info.value.code)

    def test_create_expense_multitenancy(self) -> None:
        """Usuário A não pode criar despesa com categoria do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        category_b = _setup_category(user_b)

        data: dict[str, Any] = {
            "category": category_b.uuid,
            "name": "Invasão",
            "estimated_amount": Decimal("1000.00"),
            "actual_amount": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.create(user_a.company, ExpenseIn(**data))

        assert "budget_category_not_found_or_denied" in str(exc_info.value.code)

    def test_create_expense_validation_error(self, user: Any) -> None:
        """Erro de negócio: num_installments < 1."""
        category = _setup_category(user)

        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Buffet",
            "estimated_amount": Decimal("100.00"),
            "actual_amount": Decimal("100.00"),
            "num_installments": 0,
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ExpenseService.create(user.company, ExpenseIn(**data))

        assert "invalid_installment_number" in str(exc_info.value.code)

    def test_create_expense_defaults_to_one_installment(self, user: Any) -> None:
        """Sem informar parcelamento, gera 1 parcela com vencimento hoje."""
        category = _setup_category(user)
        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Buffet",
            "estimated_amount": Decimal("1000.00"),
            "actual_amount": Decimal("1000.00"),
        }

        expense = ExpenseService.create(user.company, ExpenseIn(**data))
        assert expense.installments.count() == 1
        first = expense.installments.first()
        assert first is not None
        assert first.due_date == date.today()

    def test_create_expense_amount_differs_from_contract_raises_error(
        self, user: Any
    ) -> None:
        """BR-F02: despesa vinculada a contrato deve ter mesmo valor do contrato."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=category.wedding,
            supplier=supplier,
            total_amount=Decimal("5000.00"),
        )

        data: dict[str, Any] = {
            "category": category.uuid,
            "contract": contract.uuid,
            "name": "Despesa com contrato",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("3000.00"),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ExpenseService.create(user.company, ExpenseIn(**data))

        assert exc_info.value.code == "br_f02_violation"

    @no_type_check
    def test_create_expense_contract_from_other_wedding_raises_error(
        self, user
    ) -> None:
        """BR-L02: contrato e categoria devem pertencer ao mesmo casamento."""
        category = _setup_category(user)
        other_category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=other_category.wedding,
            supplier=supplier,
            total_amount=Decimal("5000.00"),
        )

        data: dict[str, Any] = {
            "category": category.uuid,
            "contract": contract.uuid,
            "name": "Despesa cross-wedding",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        with pytest.raises(DomainIntegrityError) as exc_info:
            ExpenseService.create(user.company, ExpenseIn(**data))

        assert exc_info.value.code == "expense_contract_wedding_mismatch"

    @no_type_check
    def test_create_expense_rejects_contract_instance_from_other_tenant(
        self,
    ) -> None:
        """Contrato pré-carregado de outro tenant deve ser rejeitado."""
        user_a = UserFactory()
        user_b = UserFactory()
        category_a = _setup_category(user_a)
        wedding_b = WeddingFactory(user_context=user_b)
        supplier_b = SupplierFactory(company=user_b.company)
        contract_b = ContractFactory(wedding=wedding_b, supplier=supplier_b)
        payload = ExpenseIn.model_construct(
            category=category_a,
            contract=contract_b,
            name="Despesa cross-tenant",
            description="",
            estimated_amount=contract_b.total_amount,
            actual_amount=contract_b.total_amount,
            num_installments=1,
            first_due_date=date.today(),
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.create(user_a.company, payload)

        assert exc_info.value.code == "contract_not_found_or_denied"

    def test_create_expense_triggers_tolerance_zero(self, user: Any) -> None:
        """BR-F01: expense com actual_amount > 0 deve gerar parcelas que somam
        exatamente o valor total."""
        category = _setup_category(user)
        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Tolerância Zero",
            "estimated_amount": Decimal("1000.00"),
            "actual_amount": Decimal("1000.00"),
            "num_installments": 3,
            "first_due_date": date.today(),
        }
        expense = ExpenseService.create(user.company, ExpenseIn(**data))
        expense.refresh_from_db()
        total = sum(i.amount for i in expense.installments.all())
        assert total == Decimal("1000.00"), (
            f"Soma das parcelas ({total}) deve ser igual a actual_amount (1000.00)"
        )


@pytest.mark.django_db
class TestExpenseServiceUpdate:
    """Testes de atualização de despesas via ExpenseService."""

    def test_update_expense_description(self, user: Any) -> None:
        """Atualização de campos simples é permitida."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            description="Antiga",
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(description="Nova Descrição"),
        )

        assert updated.description == "Nova Descrição"

    def test_update_expense_partial_fields_only_name(self, user: Any) -> None:
        """Atualização apenas do nome não redistribui parcelas nem falha."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("500.00"),
            name="Nome Antigo",
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(name="Nome Novo"),
        )

        assert updated.name == "Nome Novo"
        assert updated.actual_amount == Decimal("500.00")
        assert updated.installments.count() == 1

    def test_update_expense_cross_tenant(self, user: Any) -> None:
        """Despesa de outro tenant não pode ser atualizada."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)
        other_category = BudgetCategoryFactory(
            budget=other_budget, wedding=other_wedding
        )
        other_expense = ExpenseFactory(
            wedding=other_wedding,
            category=other_category,
            company=other_user.company,
            contract=None,
        )

        with pytest.raises(ObjectNotFoundError):
            ExpenseService.update(
                user.company,
                other_expense,
                ExpensePatchIn.model_construct(name="Hack"),
            )

    def test_update_expense_amount_with_installment_count(self, user: Any) -> None:
        """Alterar actual_amount + especificar num_installments redistribui
        com o número informado."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("600.00"),
        )
        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("200.00")
        )
        InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("200.00")
        )
        InstallmentFactory(
            expense=expense, installment_number=3, amount=Decimal("200.00")
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(
                actual_amount=Decimal("900.00"),
                num_installments=3,
                first_due_date=date.today(),
            ),
        )

        assert updated.actual_amount == Decimal("900.00")
        assert updated.installments.count() == 3
        total = sum(i.amount for i in updated.installments.all())
        assert total == Decimal("900.00")

    def test_update_amount_auto_redistribute(self, user: Any) -> None:
        """Alterar actual_amount sem num_installments redistribui parcelas."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(actual_amount=Decimal("1000.00")),
        )

        assert updated.actual_amount == Decimal("1000.00")
        total = sum(i.amount for i in updated.installments.all())
        assert total == Decimal("1000.00")

    def test_update_amount_blocked_by_paid(self, user: Any) -> None:
        """Alterar actual_amount com parcelas PAID levanta erro."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            ExpenseService.update(
                user.company,
                expense,
                ExpensePatchIn.model_construct(actual_amount=Decimal("1000.00")),
            )
        assert exc.value.code == "amount_change_blocked_by_paid"

    @no_type_check
    def test_update_expense_contract_from_other_wedding_raises_error(
        self, user
    ) -> None:
        """BR-L02: despesa não pode ser religada a contrato de outro casamento."""
        category = _setup_category(user)
        other_category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=other_category.wedding,
            supplier=supplier,
            total_amount=Decimal("500.00"),
        )
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        with pytest.raises(DomainIntegrityError) as exc_info:
            ExpenseService.update(
                user.company,
                expense,
                ExpensePatchIn(contract=contract.uuid),
            )

        assert exc_info.value.code == "expense_contract_wedding_mismatch"

    @no_type_check
    def test_update_expense_rejects_contract_instance_without_mutating(
        self, user
    ) -> None:
        """Falha de tenant não deve trocar o contrato em memória."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        current_contract = ContractFactory(wedding=category.wedding, supplier=supplier)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=current_contract,
            actual_amount=current_contract.total_amount,
        )
        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        other_supplier = SupplierFactory(company=other_user.company)
        other_contract = ContractFactory(
            wedding=other_wedding,
            supplier=other_supplier,
        )
        payload = ExpensePatchIn.model_construct(contract=other_contract)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.update(user.company, expense, payload)

        assert exc_info.value.code == "contract_not_found_or_denied"
        assert expense.contract is current_contract


@pytest.mark.django_db
class TestExpenseServiceListAndGet:
    """Testes de listagem e obtenção de despesas."""

    def test_list_expenses_multitenancy(self) -> None:
        """list() retorna apenas despesas do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        cat_a = _setup_category(user_a)
        cat_b = _setup_category(user_b)

        ExpenseFactory(
            wedding=cat_a.wedding,
            category=cat_a,
            description="Despesa A",
            contract=None,
        )
        ExpenseFactory(
            wedding=cat_b.wedding,
            category=cat_b,
            description="Despesa B",
            contract=None,
        )

        qs_a = ExpenseService.list(user_a.company)
        assert qs_a.count() == 1
        first_a = qs_a.first()
        assert first_a is not None
        assert first_a.company == user_a.company

        qs_b = ExpenseService.list(user_b.company)
        assert qs_b.count() == 1
        first_b = qs_b.first()
        assert first_b is not None
        assert first_b.company == user_b.company

    def test_list_expenses_filter_by_wedding(self, user: Any) -> None:
        """list() com wedding_id filtra por casamento."""
        cat1 = _setup_category(user)
        cat2 = _setup_category(user)

        ExpenseFactory(wedding=cat1.wedding, category=cat1, contract=None)
        ExpenseFactory(wedding=cat2.wedding, category=cat2, contract=None)

        qs = ExpenseService.list(user.company, wedding_id=cat1.wedding.uuid)
        assert qs.count() == 1

    def test_get_expense_success(self, user: Any) -> None:
        """get() retorna despesa por UUID com select_related."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
        )

        result = ExpenseService.get(user.company, expense.uuid)

        assert result.uuid == expense.uuid
        assert result.category == expense.category

    def test_get_expense_not_found(self, user: Any) -> None:
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            ExpenseService.get(user.company, uuid4())

    def test_get_expense_multitenancy(self) -> None:
        """Usuário A não pode acessar despesa do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        cat_b = _setup_category(user_b)
        expense_b = ExpenseFactory(
            wedding=cat_b.wedding,
            category=cat_b,
            contract=None,
        )

        with pytest.raises(ObjectNotFoundError):
            ExpenseService.get(user_a.company, expense_b.uuid)

    def test_get_expense_by_installment_uuid_fallback(self, user: Any) -> None:
        """Passar UUID da parcela retorna a despesa pai correspondente."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
        )
        installment = InstallmentFactory(
            expense=expense,
            company=user.company,
            wedding=category.wedding,
        )

        result = ExpenseService.get(user.company, installment.uuid)

        assert result.uuid == expense.uuid


@pytest.mark.django_db
class TestExpenseServiceDelete:
    """Testes de deleção de despesas via ExpenseService."""

    def test_delete_expense_success(self, user: Any, make_expense: Any) -> None:
        """Deleção de despesa existente é permitida."""
        expense = make_expense()

        ExpenseService.delete(user.company, expense)

        with pytest.raises(ObjectNotFoundError):
            ExpenseService.get(user.company, expense.uuid)

    def test_delete_expense_with_contract_is_allowed(self, user: Any) -> None:
        """Excluir despesa vinculada a contrato é permitido."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=category.wedding, supplier=supplier)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=contract,
            actual_amount=Decimal("5000.00"),
        )

        ExpenseService.delete(user.company, expense)

        with pytest.raises(Expense.DoesNotExist):
            Expense.objects.get(uuid=expense.uuid)

    def test_delete_expense_cross_tenant(self, user: Any) -> None:
        """Despesa de outro tenant não pode ser deletada."""

        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        other_budget = BudgetFactory(wedding=other_wedding)
        other_category = BudgetCategoryFactory(
            budget=other_budget, wedding=other_wedding
        )
        other_expense = ExpenseFactory(
            wedding=other_wedding,
            category=other_category,
            company=other_user.company,
            contract=None,
        )

        with pytest.raises(ObjectNotFoundError):
            ExpenseService.delete(user.company, instance=other_expense)


@pytest.mark.django_db
class TestExpenseServiceFromDocument:
    """Testes de criação de despesa a partir de contrato
    via ExpenseService.from_document()."""

    def test_from_document_success(self, user: Any) -> None:
        """from_document() retorna dict com dados do contrato."""
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            total_amount=Decimal("5000.00"),
            name="Buffet Premium",
        )

        result = ExpenseService.from_document(user.company, contract.uuid)

        assert result["name"] == "Buffet Premium"
        assert result["actual_amount"] == Decimal("5000.00")
        assert result["contract"] == str(contract.uuid)
        assert result["category_uuid"] is None
        assert result["num_installments"] is None
        assert result["first_due_date"] is None

    def test_from_document_contract_not_found(self, user: Any) -> None:
        """UUID de contrato inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            ExpenseService.from_document(user.company, uuid4())

    def test_from_document_multitenancy(self, user: Any) -> None:
        """Usuário A não pode acessar contrato do Usuário B."""
        user_b = UserFactory()
        wedding_b = WeddingFactory(company=user_b.company)
        supplier_b = SupplierFactory(company=user_b.company)
        contract_b = ContractFactory(
            wedding=wedding_b,
            supplier=supplier_b,
            total_amount=Decimal("5000.00"),
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.from_document(user.company, contract_b.uuid)

        assert exc_info.value.code == "contract_not_found_or_denied"


@pytest.mark.django_db
class TestExpenseServiceContractIntegration:
    """Testes de integração com Contract no ExpenseService."""

    def test_create_expense_with_contract_uuid(self, user: Any) -> None:
        """Criação de despesa vinculada a contrato via UUID."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=category.wedding,
            supplier=supplier,
            total_amount=Decimal("5000.00"),
        )

        data: dict[str, Any] = {
            "category": category.uuid,
            "contract": contract.uuid,
            "name": "Despesa com contrato",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        expense = ExpenseService.create(user.company, ExpenseIn(**data))

        assert expense.contract == contract
        assert expense.wedding == category.wedding

    def test_create_expense_with_contract_instance(self, user: Any) -> None:
        """Criação de despesa vinculada a contrato via instância."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=category.wedding,
            supplier=supplier,
        )

        data: dict[str, Any] = {
            "category": category.uuid,
            "contract": contract.uuid,
            "name": "Despesa com contrato",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        expense = ExpenseService.create(user.company, ExpenseIn(**data))
        assert expense.contract == contract

    def test_update_expense_swap_contract(self, user: Any) -> None:
        """Troca de contrato vinculado via update."""
        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract1 = ContractFactory(wedding=category.wedding, supplier=supplier)
        contract2 = ContractFactory(wedding=category.wedding, supplier=supplier)

        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=contract1,
            actual_amount=contract1.total_amount,
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=contract1.total_amount,
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(contract=contract2.uuid),
        )

        assert updated.contract == contract2

    def test_update_expense_clear_contract(self, user: Any) -> None:
        """Desvinculação de contrato (contract=None) via update."""
        from apps.logistics.tests.factories import ContractFactory, SupplierFactory

        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=category.wedding, supplier=supplier)

        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=contract,
            actual_amount=contract.total_amount,
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=contract.total_amount,
        )

        updated = ExpenseService.update(
            user.company,
            expense,
            ExpensePatchIn.model_construct(contract=None),
        )

        assert updated.contract is None


@pytest.mark.django_db
class TestExpenseServiceInstallmentDistribution:
    """Testes de rateio de parcelas com valores quebrados."""

    def test_create_expense_uneven_installments(self, user: Any) -> None:
        """R$ 100 / 3 deve criar parcelas que somam exatamente R$ 100."""
        category = _setup_category(user)
        data: dict[str, Any] = {
            "category": category.uuid,
            "name": "Rateio Quebrado",
            "estimated_amount": Decimal("100.00"),
            "actual_amount": Decimal("100.00"),
            "num_installments": 3,
            "first_due_date": date.today(),
        }
        expense = ExpenseService.create(user.company, ExpenseIn(**data))
        total = sum(i.amount for i in expense.installments.all())
        assert total == Decimal("100.00")
        assert expense.installments.count() == 3

    def test_update_redistribute_invalid_number(self, user: Any) -> None:
        """Redistribuir com num_installments < 1 levanta BusinessRuleViolation."""
        category = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("500.00")
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            ExpenseService.update(
                user.company,
                expense,
                ExpensePatchIn.model_construct(
                    actual_amount=Decimal("500.00"),
                    num_installments=0,
                ),
            )
        assert exc.value.code == "invalid_installment_number"


class TestExpenseServiceValidateContractWedding:
    """Testes isolados para o método interno _validate_contract_wedding."""

    def test_validate_contract_wedding_none(self) -> None:
        """Sucesso quando não há contrato vinculado."""
        category = SimpleNamespace(wedding_id=uuid4())
        result = ExpenseService._validate_contract_wedding(
            category=category,  # type: ignore[arg-type]
            contract=None,
        )
        assert result is None

    def test_validate_contract_wedding_same_wedding(self) -> None:
        """Sucesso quando o contrato pertence ao mesmo casamento da categoria."""
        wedding_id = uuid4()
        category = SimpleNamespace(wedding_id=wedding_id)
        contract = SimpleNamespace(wedding_id=wedding_id)

        result = ExpenseService._validate_contract_wedding(
            category=category,  # type: ignore[arg-type]
            contract=contract,  # type: ignore[arg-type]
        )
        assert result is None

    def test_validate_contract_wedding_different_wedding(self) -> None:
        """Levanta erro quando o contrato pertence a outro casamento."""
        category = SimpleNamespace(wedding_id=uuid4())
        contract = SimpleNamespace(wedding_id=uuid4())

        with pytest.raises(DomainIntegrityError) as exc:
            ExpenseService._validate_contract_wedding(
                category=category,  # type: ignore[arg-type]
                contract=contract,  # type: ignore[arg-type]
            )

        assert exc.value.code == "expense_contract_wedding_mismatch"
