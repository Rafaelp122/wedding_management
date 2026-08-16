"""
Testes unitários e de integração para Selectors do domínio financeiro.
"""

from datetime import date
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.selectors import (
    budget_category_get_selector,
    budget_category_list_selector,
    budget_get_for_wedding_selector,
    budget_get_selector,
    budget_list_selector,
    expense_get_selector,
    expense_list_selector,
    installment_get_selector,
    installment_list_selector,
)
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import (
    BudgetFactory as _BudgetFactory,
)
from apps.finances.tests.factories import (
    ExpenseFactory as _ExpenseFactory,
)
from apps.finances.tests.factories import (
    InstallmentFactory as _InstallmentFactory,
)
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def BudgetCategoryFactory(*args: Any, **kwargs: Any) -> BudgetCategory:
    return cast(BudgetCategory, _BudgetCategoryFactory(*args, **kwargs))


def BudgetFactory(*args: Any, **kwargs: Any) -> Budget:
    return cast(Budget, _BudgetFactory(*args, **kwargs))


def ExpenseFactory(*args: Any, **kwargs: Any) -> Expense:
    return cast(Expense, _ExpenseFactory(*args, **kwargs))


def InstallmentFactory(*args: Any, **kwargs: Any) -> Installment:
    return cast(Installment, _InstallmentFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestBudgetSelectors:
    """Testes para seletores de Budget."""

    def test_budget_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        budget_a = BudgetFactory(wedding=wedding_a)
        budget_b = BudgetFactory(wedding=wedding_b)

        qs_a = budget_list_selector(company=user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().uuid == budget_a.uuid

        qs_b = budget_list_selector(company=user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().uuid == budget_b.uuid

    def test_budget_list_selector_filter_by_wedding(self, user: Any) -> None:
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)

        b1 = BudgetFactory(wedding=wedding1)
        BudgetFactory(wedding=wedding2)

        qs = budget_list_selector(company=user.company, wedding_id=wedding1.uuid)
        assert list(qs) == [b1]

    def test_budget_get_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)

        result = budget_get_selector(company=user.company, uuid=budget.uuid)
        assert result.uuid == budget.uuid
        assert result.wedding == wedding

    def test_budget_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            budget_get_selector(company=user.company, uuid=uuid4())

    def test_budget_get_selector_invalid_uuid(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            budget_get_selector(company=user.company, uuid="invalid-uuid")

    def test_budget_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        wedding_b = WeddingFactory(user_context=user_b)
        budget_b = BudgetFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            budget_get_selector(company=user_a.company, uuid=budget_b.uuid)

    def test_budget_get_for_wedding_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)

        result = budget_get_for_wedding_selector(
            company=user.company, wedding_uuid=wedding.uuid
        )
        assert result.uuid == budget.uuid
        assert result.wedding == wedding

    def test_budget_get_for_wedding_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            budget_get_for_wedding_selector(company=user.company, wedding_uuid=uuid4())

    def test_budget_get_for_wedding_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        wedding_b = WeddingFactory(user_context=user_b)
        BudgetFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            budget_get_for_wedding_selector(
                company=user_a.company, wedding_uuid=wedding_b.uuid
            )


@pytest.mark.django_db
class TestBudgetCategorySelectors:
    """Testes para seletores de BudgetCategory."""

    def test_budget_category_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        wedding_a = WeddingFactory(user_context=user_a)
        budget_a = BudgetFactory(wedding=wedding_a)
        cat_a = BudgetCategoryFactory(budget=budget_a, wedding=wedding_a, name="Cat A")

        wedding_b = WeddingFactory(user_context=user_b)
        budget_b = BudgetFactory(wedding=wedding_b)
        cat_b = BudgetCategoryFactory(budget=budget_b, wedding=wedding_b, name="Cat B")

        qs_a = budget_category_list_selector(company=user_a.company)
        assert list(qs_a) == [cat_a]

        qs_b = budget_category_list_selector(company=user_b.company)
        assert list(qs_b) == [cat_b]

    def test_budget_category_list_selector_filters(self, user: Any) -> None:
        wedding1 = WeddingFactory(user_context=user)
        budget1 = BudgetFactory(wedding=wedding1)
        cat1 = BudgetCategoryFactory(budget=budget1, wedding=wedding1, name="Cat 1")

        wedding2 = WeddingFactory(user_context=user)
        budget2 = BudgetFactory(wedding=wedding2)
        BudgetCategoryFactory(budget=budget2, wedding=wedding2, name="Cat 2")

        # Filtro por budget
        qs_budget = budget_category_list_selector(
            company=user.company, budget_id=budget1.uuid
        )
        assert list(qs_budget) == [cat1]

        # Filtro por wedding
        qs_wedding = budget_category_list_selector(
            company=user.company, wedding_id=wedding1.uuid
        )
        assert list(qs_wedding) == [cat1]

    def test_budget_category_get_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        cat = BudgetCategoryFactory(budget=budget, wedding=wedding, name="Buffet")

        result = budget_category_get_selector(company=user.company, uuid=cat.uuid)
        assert result.uuid == cat.uuid
        assert result.name == "Buffet"

    def test_budget_category_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            budget_category_get_selector(company=user.company, uuid=uuid4())

    def test_budget_category_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        wedding_b = WeddingFactory(user_context=user_b)
        budget_b = BudgetFactory(wedding=wedding_b)
        cat_b = BudgetCategoryFactory(budget=budget_b, wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            budget_category_get_selector(company=user_a.company, uuid=cat_b.uuid)


@pytest.mark.django_db
class TestExpenseSelectors:
    """Testes para seletores de Expense."""

    def test_expense_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        w_a = WeddingFactory(user_context=user_a)
        b_a = BudgetFactory(wedding=w_a)
        c_a = BudgetCategoryFactory(budget=b_a, wedding=w_a)
        exp_a = ExpenseFactory(wedding=w_a, category=c_a, contract=None)

        w_b = WeddingFactory(user_context=user_b)
        b_b = BudgetFactory(wedding=w_b)
        c_b = BudgetCategoryFactory(budget=b_b, wedding=w_b)
        ExpenseFactory(wedding=w_b, category=c_b, contract=None)

        qs_a = expense_list_selector(company=user_a.company)
        assert list(qs_a) == [exp_a]

    def test_expense_list_selector_filters(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        c1 = BudgetCategoryFactory(budget=b1, wedding=w1)
        c2 = BudgetCategoryFactory(budget=b1, wedding=w1)
        exp1 = ExpenseFactory(wedding=w1, category=c1, contract=None)
        exp2 = ExpenseFactory(wedding=w1, category=c2, contract=None)

        w2 = WeddingFactory(user_context=user)
        b2 = BudgetFactory(wedding=w2)
        c3 = BudgetCategoryFactory(budget=b2, wedding=w2)
        ExpenseFactory(wedding=w2, category=c3, contract=None)

        # Filtro por wedding
        qs_w = expense_list_selector(company=user.company, wedding_id=w1.uuid)
        assert set(qs_w) == {exp1, exp2}

        # Filtro por categoria
        qs_cat = expense_list_selector(company=user.company, category_id=c1.uuid)
        assert list(qs_cat) == [exp1]

    def test_expense_get_selector_success(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)

        result = expense_get_selector(company=user.company, uuid=exp.uuid)
        assert result.uuid == exp.uuid
        assert result.category == c

    def test_expense_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            expense_get_selector(company=user.company, uuid=uuid4())

    def test_expense_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        w_b = WeddingFactory(user_context=user_b)
        b_b = BudgetFactory(wedding=w_b)
        c_b = BudgetCategoryFactory(budget=b_b, wedding=w_b)
        exp_b = ExpenseFactory(wedding=w_b, category=c_b, contract=None)

        with pytest.raises(ObjectNotFoundError):
            expense_get_selector(company=user_a.company, uuid=exp_b.uuid)

    def test_expense_get_selector_by_installment_uuid_fallback(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)
        inst = InstallmentFactory(
            expense=exp, wedding=w, company=user.company, amount=Decimal("100.00")
        )

        result = expense_get_selector(company=user.company, uuid=inst.uuid)
        assert result.uuid == exp.uuid


@pytest.mark.django_db
class TestInstallmentSelectors:
    """Testes para seletores de Installment."""

    def test_installment_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        w_a = WeddingFactory(user_context=user_a)
        b_a = BudgetFactory(wedding=w_a)
        c_a = BudgetCategoryFactory(budget=b_a, wedding=w_a)
        exp_a = ExpenseFactory(wedding=w_a, category=c_a, contract=None)
        inst_a = InstallmentFactory(expense=exp_a, wedding=w_a, company=user_a.company)

        w_b = WeddingFactory(user_context=user_b)
        b_b = BudgetFactory(wedding=w_b)
        c_b = BudgetCategoryFactory(budget=b_b, wedding=w_b)
        exp_b = ExpenseFactory(wedding=w_b, category=c_b, contract=None)
        InstallmentFactory(expense=exp_b, wedding=w_b, company=user_b.company)

        qs_a = installment_list_selector(company=user_a.company)
        assert list(qs_a) == [inst_a]

    def test_installment_list_selector_filters(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        c1 = BudgetCategoryFactory(budget=b1, wedding=w1)
        exp1 = ExpenseFactory(wedding=w1, category=c1, contract=None)
        exp2 = ExpenseFactory(wedding=w1, category=c1, contract=None)

        inst1 = InstallmentFactory(
            expense=exp1,
            wedding=w1,
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=date(2026, 8, 10),
        )
        inst2 = InstallmentFactory(
            expense=exp1,
            wedding=w1,
            company=user.company,
            status=Installment.StatusChoices.PAID,
            paid_date=date(2026, 8, 15),
            due_date=date(2026, 8, 15),
        )
        inst3 = InstallmentFactory(
            expense=exp2,
            wedding=w1,
            company=user.company,
            status=Installment.StatusChoices.OVERDUE,
            due_date=date(2026, 8, 20),
        )

        # Filtro por expense_id
        qs_exp = installment_list_selector(company=user.company, expense_id=exp1.uuid)
        assert set(qs_exp) == {inst1, inst2}

        # Filtro por wedding_id
        qs_w = installment_list_selector(company=user.company, wedding_id=w1.uuid)
        assert set(qs_w) == {inst1, inst2, inst3}

        # Filtro por status
        qs_pending = installment_list_selector(
            company=user.company, status=Installment.StatusChoices.PENDING
        )
        assert list(qs_pending) == [inst1]

        qs_paid = installment_list_selector(
            company=user.company, status=Installment.StatusChoices.PAID
        )
        assert list(qs_paid) == [inst2]

        qs_overdue = installment_list_selector(
            company=user.company, status=Installment.StatusChoices.OVERDUE
        )
        assert list(qs_overdue) == [inst3]

        # Filtro por período
        qs_range = installment_list_selector(
            company=user.company,
            due_date_gte=date(2026, 8, 12),
            due_date_lte=date(2026, 8, 18),
        )
        assert list(qs_range) == [inst2]

    def test_installment_get_selector_success(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)
        inst = InstallmentFactory(expense=exp, wedding=w, company=user.company)

        result = installment_get_selector(company=user.company, uuid=inst.uuid)
        assert result.uuid == inst.uuid
        assert result.expense == exp

    def test_installment_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            installment_get_selector(company=user.company, uuid=uuid4())

    def test_installment_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        w_b = WeddingFactory(user_context=user_b)
        b_b = BudgetFactory(wedding=w_b)
        c_b = BudgetCategoryFactory(budget=b_b, wedding=w_b)
        exp_b = ExpenseFactory(wedding=w_b, category=c_b, contract=None)
        inst_b = InstallmentFactory(expense=exp_b, wedding=w_b, company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            installment_get_selector(company=user_a.company, uuid=inst_b.uuid)
