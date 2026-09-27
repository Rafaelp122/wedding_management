from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError

from apps.core.exceptions import BusinessRuleViolation
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


def _setup_expense(user: User, **kwargs: Any) -> Expense:
    """Helper: cria wedding + budget + category + expense no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    return ExpenseFactory(wedding=wedding, category=category, contract=None, **kwargs)


@pytest.mark.django_db
class TestInstallmentModelMetadata:
    """Testes de representação e metadados do modelo Installment."""

    def test_installment_str_representation(self, user: Any) -> None:
        """__str__ deve conter número da parcela, descrição da despesa e status."""
        expense = _setup_expense(
            user, description="Buffet Premium", actual_amount=Decimal("500.00")
        )
        installment = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=3,
            amount=Decimal("500.00"),
            due_date=date.today(),
        )

        result = str(installment)
        assert "Parcela 3" in result
        assert "Buffet Premium" in result
        assert "PENDING" in result

    def test_installment_ordering_by_due_date(self, user: Any) -> None:
        """Ordenação padrão deve ser por due_date ascendente."""
        expense = _setup_expense(user, actual_amount=Decimal("1500.00"))

        i1 = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=500,
            due_date=date.today() + timedelta(days=30),
        )
        i2 = InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=500,
            due_date=date.today() + timedelta(days=10),
        )
        i3 = InstallmentFactory(
            expense=expense,
            installment_number=3,
            amount=500,
            due_date=date.today() + timedelta(days=60),
        )

        installments = list(expense.installments.all())
        assert installments == [i2, i1, i3]

    def test_installment_unique_expense_and_number(self, user: Any) -> None:
        """Não pode haver duas parcelas com mesmo número para a mesma despesa."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))

        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("500.00")
        )

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            InstallmentFactory(
                expense=expense, installment_number=1, amount=Decimal("0.00")
            )


@pytest.mark.django_db
class TestInstallmentStatusConsistency:
    """Testes de consistência paid_date ↔ status (BR-F03)."""

    def _make_installment(self, user: User, **kwargs: Any) -> Installment:
        """Helper: cria expense + constrói installment em memória."""
        expense = _setup_expense(
            user,
            actual_amount=Decimal(kwargs.get("amount", 500)),
        )
        return Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal(kwargs.get("amount", 500)),
            due_date=kwargs.get("due_date", date.today() + timedelta(days=30)),
            paid_date=kwargs.get("paid_date"),
            status=kwargs.get("status", Installment.StatusChoices.PENDING),
        )

    def test_paid_date_requires_paid_status(self, user: Any) -> None:
        """Parcela com paid_date preenchida deve ter status PAID."""
        installment = self._make_installment(
            user,
            paid_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )

        with pytest.raises(ValidationError) as exc_info:
            installment.full_clean()

        assert "PAGO" in str(exc_info.value).upper()

    def test_paid_status_requires_paid_date(self, user: Any) -> None:
        """Parcela com status PAID deve ter paid_date preenchida."""
        installment = self._make_installment(
            user,
            paid_date=None,
            status=Installment.StatusChoices.PAID,
        )

        with pytest.raises(ValidationError) as exc_info:
            installment.full_clean()

        assert "data de pagamento" in str(exc_info.value).lower()

    def test_overdue_with_paid_date_fails(self, user: Any) -> None:
        """Parcela com paid_date preenchida deve ter status PAID, não OVERDUE."""
        installment = self._make_installment(
            user,
            paid_date=date.today(),
            status=Installment.StatusChoices.OVERDUE,
        )

        with pytest.raises(ValidationError):
            installment.full_clean()

    def test_pending_without_paid_date_passes(self, user: Any) -> None:
        """Parcela PENDING sem paid_date é válida."""
        installment = self._make_installment(
            user,
            paid_date=None,
            status=Installment.StatusChoices.PENDING,
            due_date=date.today() + timedelta(days=30),
        )
        installment.full_clean()

    def test_paid_with_paid_date_passes(self, user: Any) -> None:
        """Parcela PAID com paid_date é válida."""
        installment = self._make_installment(
            user,
            paid_date=date.today(),
            status=Installment.StatusChoices.PAID,
            due_date=date.today() - timedelta(days=5),
        )
        installment.full_clean()


@pytest.mark.django_db
class TestInstallmentAmountValidator:
    """Testes de validação do valor da parcela."""

    def test_installment_amount_negative_fails(self, user: Any) -> None:
        """Valor negativo deve levantar ValidationError."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("-100.00"),
            due_date=date.today(),
        )

        with pytest.raises(ValidationError):
            installment.full_clean()


@pytest.mark.django_db
class TestInstallmentTransitions:
    """Testes da máquina de estados e transições de Installment."""

    def test_allowed_transitions_matrix(self) -> None:
        """Verifica se a matriz de transições permitidas está correta."""
        assert Installment.ALLOWED_TRANSITIONS == {
            Installment.StatusChoices.PENDING: {
                Installment.StatusChoices.PAID,
                Installment.StatusChoices.OVERDUE,
            },
            Installment.StatusChoices.OVERDUE: {
                Installment.StatusChoices.PAID,
                Installment.StatusChoices.PENDING,
            },
            Installment.StatusChoices.PAID: {
                Installment.StatusChoices.PENDING,
                Installment.StatusChoices.OVERDUE,
            },
        }

    def test_can_transition_to(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        assert inst.can_transition_to(Installment.StatusChoices.PAID) is True
        assert inst.can_transition_to(Installment.StatusChoices.OVERDUE) is True
        assert inst.can_transition_to("UNKNOWN") is False

    def test_transition_to_valid(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        inst.transition_to(Installment.StatusChoices.OVERDUE)
        assert inst.status == Installment.StatusChoices.OVERDUE

    def test_transition_to_same_status_noop(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        inst.transition_to(Installment.StatusChoices.PENDING)
        assert inst.status == Installment.StatusChoices.PENDING

    def test_transition_to_invalid_raises_violation(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            inst.transition_to("INVALID_STATUS")
        assert exc_info.value.code == "installment_invalid_status_transition"
        assert "Não é permitido transitar" in str(exc_info.value.detail)


@pytest.mark.django_db
class TestInstallmentSemanticMethods:
    """Testes dos métodos semânticos de ciclo de vida de Installment."""

    def test_mark_as_paid_success(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        custom_date = date.today() - timedelta(days=2)
        inst.mark_as_paid(paid_date=custom_date)

        assert inst.status == Installment.StatusChoices.PAID
        assert inst.paid_date == custom_date

    def test_mark_as_paid_default_today(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        inst.mark_as_paid()
        assert inst.paid_date == date.today()
        assert inst.status == Installment.StatusChoices.PAID

    def test_mark_as_paid_already_paid_raises_violation(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            paid_date=date.today(),
            status=Installment.StatusChoices.PAID,
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            inst.mark_as_paid()
        assert exc_info.value.code == "installment_already_paid"

    def test_unmark_as_paid_future_due_date_transitions_to_pending(
        self, user: Any
    ) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=5),
            paid_date=date.today(),
            status=Installment.StatusChoices.PAID,
        )
        inst.unmark_as_paid()
        assert inst.status == Installment.StatusChoices.PENDING
        assert inst.paid_date is None

    def test_unmark_as_paid_past_due_date_transitions_to_overdue(
        self, user: Any
    ) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() - timedelta(days=5),
            paid_date=date.today(),
            status=Installment.StatusChoices.PAID,
        )
        inst.unmark_as_paid()
        assert inst.status == Installment.StatusChoices.OVERDUE
        assert inst.paid_date is None

    def test_unmark_as_paid_not_paid_raises_violation(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PENDING,
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            inst.unmark_as_paid()
        assert exc_info.value.code == "installment_not_paid"

    def test_mark_as_overdue_success(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() - timedelta(days=1),
            status=Installment.StatusChoices.PENDING,
        )
        inst.mark_as_overdue()
        assert inst.status == Installment.StatusChoices.OVERDUE

    def test_mark_as_overdue_future_due_date_raises_violation(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=2),
            status=Installment.StatusChoices.PENDING,
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            inst.mark_as_overdue()
        assert exc_info.value.code == "installment_not_overdue"


@pytest.mark.django_db
class TestInstallmentDomainProperties:
    """Testes de propriedades ativas em Installment."""

    def test_is_late_flag(self, user: Any) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst_late = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() - timedelta(days=2),
            status=Installment.StatusChoices.PENDING,
        )
        assert inst_late.is_late is True

        inst_ontime = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=2,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=2),
            status=Installment.StatusChoices.PENDING,
        )
        assert inst_ontime.is_late is False

        inst_paid_past = Installment(
            company=user.company,
            wedding=expense.wedding,
            expense=expense,
            installment_number=3,
            amount=Decimal("500.00"),
            due_date=date.today() - timedelta(days=2),
            paid_date=date.today(),
            status=Installment.StatusChoices.PAID,
        )
        assert inst_paid_past.is_late is False

    def test_paid_installment_immutability(self, user: Any) -> None:
        """clean() impede alteração de dados em parcelas já pagas."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today(),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        inst.amount = Decimal("600.00")
        with pytest.raises(ValidationError) as excinfo:
            inst.clean()
        assert "Parcelas pagas não podem" in str(excinfo.value)

        inst.amount = Decimal("500.00")
        inst.due_date = date.today() + timedelta(days=5)
        with pytest.raises(ValidationError) as excinfo:
            inst.clean()
        assert "Parcelas pagas não podem" in str(excinfo.value)

        inst.due_date = date.today()
        inst.installment_number = 2
        with pytest.raises(ValidationError) as excinfo:
            inst.clean()
        assert "Parcelas pagas não podem" in str(excinfo.value)

    def test_validate_chronology_boundaries(self, user: Any) -> None:
        """validate_chronology valida precedência temporal com parcelas vizinhas."""
        expense = _setup_expense(user, actual_amount=Decimal("900.00"))
        base_date = date.today()

        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("300.00"),
            due_date=base_date,
        )
        i2 = InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("300.00"),
            due_date=base_date + timedelta(days=30),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=3,
            amount=Decimal("300.00"),
            due_date=base_date + timedelta(days=60),
        )

        # Retorna sem erro se expense_id ou installment_number for None
        unlinked = Installment()
        unlinked.validate_chronology(base_date)

        # Tentar mover i2 para antes de i1
        with pytest.raises(BusinessRuleViolation) as excinfo:
            i2.validate_chronology(base_date - timedelta(days=1))
        assert excinfo.value.code == "due_date_before_previous_installment"

        # Tentar mover i2 para depois de i3
        with pytest.raises(BusinessRuleViolation) as excinfo:
            i2.validate_chronology(base_date + timedelta(days=65))
        assert excinfo.value.code == "due_date_after_next_installment"
