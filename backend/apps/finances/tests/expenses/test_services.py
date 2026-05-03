from decimal import Decimal
from uuid import uuid4

import pytest

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_category(user):
    """Helper: cria wedding + budget + category no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    return category


@pytest.mark.django_db
class TestExpenseServiceCreate:
    """Testes de criação de despesas via ExpenseService."""

    def test_create_expense_success(self, user):
        """Criação de despesa válida com categoria."""
        category = _setup_category(user)

        data = {
            "category": category.uuid,
            "description": "Buffet Premium",
            "estimated_amount": Decimal("10000.00"),
            "actual_amount": Decimal("10000.00"),
        }

        expense = ExpenseService.create(user.company, data)

        assert expense.category == category
        assert expense.wedding == category.wedding
        assert expense.description == "Buffet Premium"
        assert expense.actual_amount == Decimal("10000.00")

    def test_create_expense_with_category_instance(self, user):
        """create() aceita instância de BudgetCategory, não só UUID."""
        category = _setup_category(user)

        data = {
            "category": category,
            "description": "Fotografia",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        expense = ExpenseService.create(user.company, data)
        assert expense.category == category

    def test_create_expense_inherits_wedding_from_category(self, user):
        """Expense.wedding é injetado a partir da categoria."""
        category = _setup_category(user)

        expense = ExpenseService.create(
            user.company,
            {
                "category": category.uuid,
                "description": "Decoração",
                "estimated_amount": Decimal("3000.00"),
                "actual_amount": Decimal("3000.00"),
            },
        )

        assert expense.wedding == category.wedding

    def test_create_expense_category_not_found(self, user):
        """UUID de categoria inexistente levanta ObjectNotFoundError."""
        data = {
            "category": uuid4(),
            "description": "Fantasminha",
            "estimated_amount": Decimal("100.00"),
            "actual_amount": Decimal("100.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.create(user.company, data)

        assert "budget_category_not_found_or_denied" in str(exc_info.value.code)

    def test_create_expense_multitenancy(self):
        """Usuário A não pode criar despesa com categoria do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        category_b = _setup_category(user_b)

        data = {
            "category": category_b.uuid,
            "description": "Invasão",
            "estimated_amount": Decimal("1000.00"),
            "actual_amount": Decimal("1000.00"),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            ExpenseService.create(user_a.company, data)

        assert "budget_category_not_found_or_denied" in str(exc_info.value.code)

    def test_create_expense_validation_error(self, user):
        """Dados inválidos levantam BusinessRuleViolation."""
        category = _setup_category(user)

        data = {
            "category": category.uuid,
            "description": "",
            "estimated_amount": Decimal("100.00"),
            "actual_amount": Decimal("100.00"),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            ExpenseService.create(user.company, data)

        assert "expense_validation_error" in str(exc_info.value.code)

    def test_create_expense_incomplete_installment_params(self, user):
        """Erro ao enviar apenas um dos parâmetros de parcelamento."""
        category = _setup_category(user)
        data = {
            "category": category.uuid,
            "description": "Buffet",
            "estimated_amount": Decimal("1000.00"),
            "actual_amount": Decimal("1000.00"),
            "num_installments": 3,
            # Faltando first_due_date
        }

        with pytest.raises(BusinessRuleViolation) as exc:
            ExpenseService.create(user.company, data)
        assert exc.value.code == "incomplete_installment_params"


@pytest.mark.django_db
class TestExpenseServiceUpdate:
    """Testes de atualização de despesas via ExpenseService."""

    def test_update_expense_description(self, user):
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
            user.company, expense, {"description": "Nova Descrição"}
        )

        assert updated.description == "Nova Descrição"

    def test_update_expense_cannot_change_category(self, user):
        """Categoria é bloqueada no update (campo estrutural)."""
        category1 = _setup_category(user)
        category2 = _setup_category(user)
        expense = ExpenseFactory(
            wedding=category1.wedding,
            category=category1,
            contract=None,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(
            user.company, expense, {"category": category2.uuid}
        )

        assert updated.category == category1

    def test_update_expense_cannot_change_company(self, user):
        """Company é bloqueada no update."""
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
        other_user = UserFactory()

        updated = ExpenseService.update(
            user.company, expense, {"company": other_user.company}
        )

        assert updated.company == user.company


@pytest.mark.django_db
class TestExpenseServiceListAndGet:
    """Testes de listagem e obtenção de despesas."""

    def test_list_expenses_multitenancy(self):
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
        assert qs_a.first().company == user_a.company

        qs_b = ExpenseService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().company == user_b.company

    def test_list_expenses_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        cat1 = _setup_category(user)
        cat2 = _setup_category(user)

        ExpenseFactory(wedding=cat1.wedding, category=cat1, contract=None)
        ExpenseFactory(wedding=cat2.wedding, category=cat2, contract=None)

        qs = ExpenseService.list(user.company, wedding_id=cat1.wedding.uuid)
        assert qs.count() == 1

    def test_get_expense_success(self, user):
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

    def test_get_expense_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            ExpenseService.get(user.company, uuid4())

    def test_get_expense_multitenancy(self):
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


@pytest.mark.django_db
class TestExpenseServiceContractIntegration:
    """Testes de integração com Contract no ExpenseService."""

    def test_create_expense_with_contract_uuid(self, user):
        """Criação de despesa vinculada a contrato via UUID."""
        from apps.logistics.tests.factories import ContractFactory, SupplierFactory

        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=category.wedding,
            supplier=supplier,
            total_amount=Decimal("5000.00"),
        )

        data = {
            "category": category.uuid,
            "contract": contract.uuid,
            "description": "Despesa com contrato",
            "estimated_amount": Decimal("5000.00"),
            "actual_amount": Decimal("5000.00"),
        }

        expense = ExpenseService.create(user.company, data)

        assert expense.contract == contract
        assert expense.wedding == category.wedding

    def test_create_expense_with_contract_instance(self, user):
        """Criação de despesa vinculada a contrato via instância."""
        from apps.logistics.tests.factories import ContractFactory, SupplierFactory

        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(
            wedding=category.wedding,
            supplier=supplier,
        )

        data = {
            "category": category.uuid,
            "contract": contract,
            "description": "Despesa com contrato instância",
            "estimated_amount": Decimal("3000.00"),
            "actual_amount": Decimal("3000.00"),
        }

        expense = ExpenseService.create(user.company, data)
        assert expense.contract == contract

    def test_update_expense_swap_contract(self, user):
        """Troca de contrato vinculado via update."""
        from apps.logistics.tests.factories import ContractFactory, SupplierFactory

        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract1 = ContractFactory(wedding=category.wedding, supplier=supplier)
        contract2 = ContractFactory(wedding=category.wedding, supplier=supplier)

        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=contract1,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(
            user.company, expense, {"contract": contract2.uuid}
        )

        assert updated.contract == contract2

    def test_update_expense_clear_contract(self, user):
        """Desvinculação de contrato (contract=None) via update."""
        from apps.logistics.tests.factories import ContractFactory, SupplierFactory

        category = _setup_category(user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=category.wedding, supplier=supplier)

        expense = ExpenseFactory(
            wedding=category.wedding,
            category=category,
            contract=contract,
            actual_amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )

        updated = ExpenseService.update(user.company, expense, {"contract": None})

        assert updated.contract is None
