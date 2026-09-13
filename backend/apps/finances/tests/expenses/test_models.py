from decimal import Decimal
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import BudgetFactory as _BudgetFactory
from apps.finances.tests.factories import ExpenseFactory as _ExpenseFactory
from apps.finances.tests.factories import InstallmentFactory as _InstallmentFactory
from apps.users.models import User
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


def _setup_expense(user: User) -> tuple[Wedding, BudgetCategory]:
    """Helper: cria wedding + budget + category no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    return wedding, category


def _make_expense(user: User, category: BudgetCategory, **kwargs: Any) -> Expense:
    """Helper: cria expense vinculado ao wedding da categoria."""
    return ExpenseFactory(
        wedding=category.wedding, category=category, contract=None, **kwargs
    )


@pytest.mark.django_db
class TestExpenseModelMetadata:
    """Testes de representação e metadados do modelo Expense."""

    def test_expense_ordering_by_created_at_descending(self, user: Any) -> None:
        """Ordenação padrão deve ser por -created_at (mais recente primeiro)."""
        _, category = _setup_expense(user)
        e1 = _make_expense(user, category, description="Despesa Antiga")
        e2 = _make_expense(user, category, description="Despesa Nova")

        expenses = list(Expense.objects.all())
        assert expenses[0] == e2
        assert expenses[1] == e1

    def test_expense_str_representation(self, user: Any) -> None:
        """__str__ deve conter o nome da despesa."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, name="Buffet Premium")
        result = str(expense)
        assert "Buffet Premium" in result


@pytest.mark.django_db
class TestExpenseToleranceZero:
    """Testes da regra de Tolerância Zero (ADR-010 / BR-F01)."""

    def test_expense_clean_passes_when_sum_matches(self, user: Any) -> None:
        """Soma das parcelas == actual_amount deve passar na validação."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("333.33")
        )
        InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("333.33")
        )
        InstallmentFactory(
            expense=expense, installment_number=3, amount=Decimal("333.34")
        )

        expense.full_clean()

    def test_expense_clean_fails_when_sum_mismatch(self, user: Any) -> None:
        """Soma das parcelas != actual_amount deve levantar ValidationError."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("400.00")
        )
        InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("400.00")
        )

        with pytest.raises(ValidationError) as exc_info:
            expense.full_clean()

        assert "não bate" in str(exc_info.value).lower()

    def test_expense_clean_passes_with_zero_actual_amount(self, user: Any) -> None:
        """Despesa com actual_amount = 0 deve passar (sem parcelas)."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("0.00"))
        expense.full_clean()

    def test_expense_clean_when_no_installments(self, user: Any) -> None:
        """Sem parcelas criadas e actual_amount > 0: soma = 0, deve falhar."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("500.00"))

        with pytest.raises(ValidationError) as exc_info:
            expense.full_clean()

        assert "não bate" in str(exc_info.value).lower()

    def test_expense_creation_skips_tolerance_validation(self, user: Any) -> None:
        """Criação (primeiro save) não valida Tolerância Zero — gap intencional.

        O guard self.pk em Expense.clean() impede a validação durante o
        primeiro save porque as parcelas ainda não existem. O service layer
        (ExpenseService.create) é responsável por gerar as parcelas via
        InstallmentService.auto_generate_installments() após o save.

        Este teste documenta o comportamento esperado: criação via modelo
        direto (sem service layer) com actual_amount > 0 e sem parcelas
        passa no primeiro save mas falha em full_clean() posterior.
        """
        _, category = _setup_expense(user)
        expense = Expense(
            company=category.wedding.company,
            wedding=category.wedding,
            category=category,
            contract=None,
            name="Teste gap criação",
            estimated_amount=Decimal("500.00"),
            actual_amount=Decimal("500.00"),
        )

        assert expense.pk is None
        expense.save()
        assert expense.pk is not None

        with pytest.raises(ValidationError) as exc_info:
            expense.full_clean()

        assert "não bate" in str(exc_info.value).lower()


@pytest.mark.django_db
class TestExpenseDomainProperties:
    """Testes das propriedades de domínio ricas do modelo Expense."""

    def test_is_settled_and_partially_paid_with_relations(self, user: Any) -> None:
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        i1 = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PENDING,
        )
        i2 = InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert expense.is_settled is False
        assert expense.is_partially_paid is False
        assert expense.balance_due == Decimal("1000.00")
        assert expense.payment_progress_percent == 0

        # Paga a primeira parcela
        i1.mark_as_paid()
        i1.save()

        assert expense.is_settled is False
        assert expense.is_partially_paid is True
        assert expense.balance_due == Decimal("500.00")
        assert expense.payment_progress_percent == 50

        # Paga a segunda parcela
        i2.mark_as_paid()
        i2.save()

        assert expense.is_settled is True
        assert expense.is_partially_paid is False
        assert expense.balance_due == Decimal("0.00")
        assert expense.payment_progress_percent == 100

    def test_properties_with_annotated_attributes(self, user: Any) -> None:
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        # Simula anotações do queryset with_details()
        expense.installments_count = 4  # type: ignore[attr-defined]
        expense.paid_installments_count = 2  # type: ignore[attr-defined]
        expense.total_paid = Decimal("500.00")  # type: ignore[attr-defined]

        assert expense.is_settled is False
        assert expense.is_partially_paid is True
        assert expense.balance_due == Decimal("500.00")
        assert expense.payment_progress_percent == 50

        # Simula todas pagas
        expense.paid_installments_count = 4  # type: ignore[attr-defined]
        expense.total_paid = Decimal("1000.00")  # type: ignore[attr-defined]

        assert expense.is_settled is True
        assert expense.is_partially_paid is False
        assert expense.balance_due == Decimal("0.00")
        assert expense.payment_progress_percent == 100

    def test_payment_progress_percent_zero_amount(self, user: Any) -> None:
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("0.00"))
        assert expense.payment_progress_percent == 0
        assert expense.is_settled is False
        assert expense.is_partially_paid is False
