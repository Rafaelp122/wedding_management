from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Protocol, cast

import pytest

from apps.finances.managers import (
    BudgetCategoryQuerySet,
    BudgetQuerySet,
    ExpenseQuerySet,
    InstallmentQuerySet,
)
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
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


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


class _ExpenseDetails(Protocol):
    installments_count: int
    paid_installments_count: int
    total_paid: Decimal
    total_pending: Decimal


def _setup_expense(user: Any) -> tuple[Any, Expense]:
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    expense = ExpenseFactory(
        wedding=wedding, category=category, actual_amount=Decimal("1500.00")
    )
    return wedding, expense


@pytest.mark.django_db
class TestBudgetQuerySet:
    """Testes para os métodos encadeáveis do BudgetQuerySet."""

    def test_for_wedding_filters_correctly(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        w2 = WeddingFactory(user_context=user)

        b1 = BudgetFactory(wedding=w1)
        BudgetFactory(wedding=w2)

        qs_inst = Budget.objects.for_tenant(user.company).for_wedding(w1)
        assert list(qs_inst) == [b1]

        qs_uuid = Budget.objects.for_tenant(user.company).for_wedding(w1.uuid)
        assert list(qs_uuid) == [b1]

        qs_str = Budget.objects.for_tenant(user.company).for_wedding(str(w1.uuid))
        assert list(qs_str) == [b1]

        qs_int = Budget.objects.for_tenant(user.company).for_wedding(w1.id)
        assert list(qs_int) == [b1]

        qs_none = Budget.objects.for_tenant(user.company).for_wedding(None)
        assert qs_none.count() == 2

    def test_with_total_spent(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(
            wedding=w, category=c, actual_amount=Decimal("1000.00"), contract=None
        )
        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            amount=Decimal("400.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )
        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            amount=Decimal("600.00"),
            status=Installment.StatusChoices.PENDING,
        )

        qs = Budget.objects.for_tenant(user.company).with_total_spent()
        assert isinstance(qs, BudgetQuerySet)
        res = qs.get(uuid=b.uuid)
        assert res.total_overall_spent == Decimal("400.00")


@pytest.mark.django_db
class TestBudgetCategoryQuerySet:
    """Testes para os métodos encadeáveis do BudgetCategoryQuerySet."""

    def test_for_budget_and_wedding(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        c1 = BudgetCategoryFactory(budget=b1, wedding=w1, name="Cat W1")

        w2 = WeddingFactory(user_context=user)
        b2 = BudgetFactory(wedding=w2)
        BudgetCategoryFactory(budget=b2, wedding=w2, name="Cat W2")

        qs_b = BudgetCategory.objects.for_tenant(user.company).for_budget(b1)
        assert isinstance(qs_b, BudgetCategoryQuerySet)
        assert list(qs_b) == [c1]

        qs_b_uuid = BudgetCategory.objects.for_tenant(user.company).for_budget(b1.uuid)
        assert list(qs_b_uuid) == [c1]

        qs_w = BudgetCategory.objects.for_tenant(user.company).for_wedding(w1)
        assert list(qs_w) == [c1]

        qs_w_uuid = BudgetCategory.objects.for_tenant(user.company).for_wedding(w1.uuid)
        assert list(qs_w_uuid) == [c1]

    def test_with_total_spent(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(
            wedding=w, category=c, actual_amount=Decimal("500.00"), contract=None
        )
        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            amount=Decimal("200.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        qs = BudgetCategory.objects.for_tenant(user.company).with_total_spent()
        res = qs.get(uuid=c.uuid)
        assert res.total_spent == Decimal("200.00")


@pytest.mark.django_db
class TestExpenseQuerySet:
    def test_with_details_returns_expense_queryset(self, user: Any) -> None:
        _setup_expense(user)

        qs = Expense.objects.for_tenant(user.company).with_details()

        assert isinstance(qs, ExpenseQuerySet)
        assert qs.count() == 1

    def test_with_details_counts_mixed_installment_statuses(self, user: Any) -> None:
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PENDING,
        )
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.OVERDUE,
        )

        result = cast(
            _ExpenseDetails,
            (
                Expense.objects.for_tenant(user.company)
                .with_details()
                .get(uuid=expense.uuid)
            ),
        )

        assert result.installments_count == 3
        assert result.paid_installments_count == 1
        assert result.total_paid == Decimal("500.00")
        assert result.total_pending == Decimal("1000.00")

    def test_with_details_all_paid(self, user: Any) -> None:
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        result = cast(
            _ExpenseDetails,
            (
                Expense.objects.for_tenant(user.company)
                .with_details()
                .get(uuid=expense.uuid)
            ),
        )

        assert result.installments_count == 1
        assert result.paid_installments_count == 1
        assert result.total_paid == Decimal("1000.00")
        assert result.total_pending == Decimal("0.00")

    def test_with_details_all_pending(self, user: Any) -> None:
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        result = cast(
            _ExpenseDetails,
            (
                Expense.objects.for_tenant(user.company)
                .with_details()
                .get(uuid=expense.uuid)
            ),
        )

        assert result.total_paid == Decimal("0.00")
        assert result.total_pending == Decimal("1000.00")

    def test_with_details_no_installments(self, user: Any) -> None:
        _, expense = _setup_expense(user)

        result = cast(
            _ExpenseDetails,
            (
                Expense.objects.for_tenant(user.company)
                .with_details()
                .get(uuid=expense.uuid)
            ),
        )

        assert result.installments_count == 0
        assert result.paid_installments_count == 0
        assert result.total_paid == Decimal("0.00")
        assert result.total_pending == Decimal("0.00")

    def test_by_category_and_for_wedding(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        c1 = BudgetCategoryFactory(budget=b1, wedding=w1)
        c2 = BudgetCategoryFactory(budget=b1, wedding=w1)
        e1 = ExpenseFactory(wedding=w1, category=c1, contract=None)
        e2 = ExpenseFactory(wedding=w1, category=c2, contract=None)

        w2 = WeddingFactory(user_context=user)
        b2 = BudgetFactory(wedding=w2)
        c3 = BudgetCategoryFactory(budget=b2, wedding=w2)
        ExpenseFactory(wedding=w2, category=c3, contract=None)

        qs_cat = Expense.objects.for_tenant(user.company).by_category(c1)
        assert list(qs_cat) == [e1]

        qs_cat_uuid = Expense.objects.for_tenant(user.company).by_category(c1.uuid)
        assert list(qs_cat_uuid) == [e1]

        qs_wed = Expense.objects.for_tenant(user.company).for_wedding(w1)
        assert set(qs_wed) == {e1, e2}

        qs_wed_uuid = Expense.objects.for_tenant(user.company).for_wedding(w1.uuid)
        assert set(qs_wed_uuid) == {e1, e2}

    def test_in_date_range(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        e = ExpenseFactory(wedding=w, category=c, contract=None)

        today = date.today()
        qs_in = Expense.objects.for_tenant(user.company).in_date_range(
            start_date=today - timedelta(days=1),
            end_date=today + timedelta(days=1),
        )
        assert list(qs_in) == [e]

        qs_out = Expense.objects.for_tenant(user.company).in_date_range(
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=10),
        )
        assert list(qs_out) == []


@pytest.mark.django_db
class TestInstallmentQuerySet:
    """Testes para os métodos encadeáveis do InstallmentQuerySet."""

    def test_status_filters(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)

        inst_pending = InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            status=Installment.StatusChoices.PENDING,
        )
        inst_paid = InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )
        inst_overdue = InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            status=Installment.StatusChoices.OVERDUE,
        )

        qs = Installment.objects.for_tenant(user.company)
        assert isinstance(qs, InstallmentQuerySet)
        assert list(qs.pending()) == [inst_pending]
        assert list(qs.paid()) == [inst_paid]
        assert list(qs.overdue()) == [inst_overdue]

    def test_due_in_next_days(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)

        today = date(2026, 8, 16)
        inst_near = InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            due_date=today + timedelta(days=3),
        )
        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            due_date=today + timedelta(days=15),
        )

        qs = Installment.objects.for_tenant(user.company).due_in_next_days(
            days=7, today=today
        )
        assert list(qs) == [inst_near]

    def test_due_in_range(self, user: Any) -> None:
        w = WeddingFactory(user_context=user)
        b = BudgetFactory(wedding=w)
        c = BudgetCategoryFactory(budget=b, wedding=w)
        exp = ExpenseFactory(wedding=w, category=c, contract=None)

        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            due_date=date(2026, 8, 5),
        )
        inst_mid = InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            due_date=date(2026, 8, 15),
        )
        InstallmentFactory(
            expense=exp,
            wedding=w,
            company=user.company,
            due_date=date(2026, 8, 25),
        )

        qs = Installment.objects.for_tenant(user.company).due_in_range(
            start_date=date(2026, 8, 10),
            end_date=date(2026, 8, 20),
        )
        assert list(qs) == [inst_mid]

    def test_for_wedding_and_for_expense(self, user: Any) -> None:
        w1 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        c1 = BudgetCategoryFactory(budget=b1, wedding=w1)
        exp1 = ExpenseFactory(wedding=w1, category=c1, contract=None)
        exp2 = ExpenseFactory(wedding=w1, category=c1, contract=None)

        inst1 = InstallmentFactory(expense=exp1, wedding=w1, company=user.company)
        inst2 = InstallmentFactory(expense=exp2, wedding=w1, company=user.company)

        qs_exp = Installment.objects.for_tenant(user.company).for_expense(exp1)
        assert list(qs_exp) == [inst1]

        qs_wed = Installment.objects.for_tenant(user.company).for_wedding(w1)
        assert set(qs_wed) == {inst1, inst2}
