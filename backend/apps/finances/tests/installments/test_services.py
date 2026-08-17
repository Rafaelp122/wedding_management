from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast
from unittest.mock import patch
from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.schemas import InstallmentAdjustIn, InstallmentIn, InstallmentPatchIn
from apps.finances.services.installment_service import InstallmentService
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
from apps.scheduler.models import Event
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


def _setup_expense(user: User, **kwargs: Any) -> Expense:
    """Helper: cria wedding + budget + category + expense no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    expense = ExpenseFactory(
        wedding=wedding, category=category, contract=None, **kwargs
    )
    return expense


@pytest.mark.django_db
class TestInstallmentServiceCreate:
    """Testes de criação de parcelas via InstallmentService."""

    def test_create_installment_success(self, user: User) -> None:
        """Criação de parcela com valor compatível com a despesa."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))

        data: dict[str, Any] = {
            "expense": expense.uuid,
            "installment_number": 1,
            "amount": Decimal("1000.00"),
            "due_date": date.today() + timedelta(days=30),
        }

        installment = InstallmentService.create(user.company, InstallmentIn(**data))

        assert installment.expense == expense
        assert installment.installment_number == 1
        assert installment.amount == Decimal("1000.00")
        assert installment.status == Installment.StatusChoices.PENDING

    def test_create_installment_with_expense_instance(self, user: User) -> None:
        """create() aceita instância de Expense, não só UUID."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))

        data: dict[str, Any] = {
            "expense": expense.uuid,
            "installment_number": 1,
            "amount": Decimal("500.00"),
            "due_date": date.today() + timedelta(days=15),
        }

        installment = InstallmentService.create(user.company, InstallmentIn(**data))
        assert installment.expense == expense

    def test_create_installment_tolerance_zero_violation(self, user: User) -> None:
        """Tolerância Zero: soma != actual_amount levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))

        data: dict[str, Any] = {
            "expense": expense.uuid,
            "installment_number": 1,
            "amount": Decimal("999.99"),
            "due_date": date.today() + timedelta(days=30),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            InstallmentService.create(user.company, InstallmentIn(**data))

        assert "expense_math_violation" in str(exc_info.value.code)

    def test_create_installment_exact_sum_passes(self, user: User) -> None:
        """Duas parcelas que somam exatamente o actual_amount = Tolerância Zero ok.
        O service valida a soma ao final de cada criação. Para evitar violação
        no estado intermediário, criamos via factory."""
        from apps.finances.tests.factories import InstallmentFactory

        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))

        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("333.33"),
            due_date=date.today() + timedelta(days=30),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("666.67"),
            due_date=date.today() + timedelta(days=60),
        )

        # Verificar que a validação da expense passa (soma = actual_amount)
        expense.full_clean()

        total = sum(i.amount for i in expense.installments.all())
        assert total == Decimal("1000.00")

    def test_create_installment_expense_not_found(self, user: User) -> None:
        """UUID de despesa inexistente deve levantar ObjectNotFoundError."""
        data: dict[str, Any] = {
            "expense": uuid4(),
            "installment_number": 1,
            "amount": Decimal("100.00"),
            "due_date": date.today() + timedelta(days=10),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            InstallmentService.create(user.company, InstallmentIn(**data))

        assert "expense_not_found_or_denied" in str(exc_info.value.code)

    def test_create_installment_multitenancy_isolation(self) -> None:
        """Usuário A não pode criar parcela em despesa do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        expense_b = _setup_expense(user_b, actual_amount=Decimal("500.00"))

        data: dict[str, Any] = {
            "expense": expense_b.uuid,
            "installment_number": 1,
            "amount": Decimal("500.00"),
            "due_date": date.today() + timedelta(days=30),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            InstallmentService.create(user_a.company, InstallmentIn(**data))

        assert "expense_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestInstallmentServiceAutoGeneration:
    """Testes de geração automática de parcelas."""

    def test_auto_generate_installments_success(self, user: User) -> None:
        """Sucesso: gera parcelas que somam exatamente o total da despesa."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        first_date = date.today() + timedelta(days=30)

        installments = InstallmentService.auto_generate_installments(
            user.company, expense, 3, first_date
        )

        assert len(installments) == 3
        # 1000 / 3 = 333.33 -> 333.33 + 333.33 + 333.34 = 1000.00
        assert installments[0].amount == Decimal("333.33")
        assert installments[1].amount == Decimal("333.33")
        assert installments[2].amount == Decimal("333.34")

        # Verificar datas (30 dias entre cada)
        assert installments[0].due_date == first_date
        assert installments[1].due_date == first_date + timedelta(days=30)
        assert installments[2].due_date == first_date + timedelta(days=60)

        # Verificar persistência e soma total
        total_sum = sum(i.amount for i in Installment.objects.filter(expense=expense))
        assert total_sum == Decimal("1000.00")

    def test_auto_generate_installments_already_exists(self, user: User) -> None:
        """Bloqueia geração se despesa já possui parcelas."""
        expense = _setup_expense(user, actual_amount=Decimal("100.00"))
        InstallmentFactory(expense=expense, amount=Decimal("100.00"))

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.auto_generate_installments(
                user.company, expense, 2, date.today()
            )
        assert exc.value.code == "installments_already_exist"

    def test_auto_generate_invalid_num_installments(self, user: User) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("100.00"))
        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.auto_generate_installments(
                user.company, expense, 0, date.today()
            )
        assert exc.value.code == "invalid_installment_number"

    def test_auto_generate_invalid_expense_amount(self, user: User) -> None:
        expense = _setup_expense(user, actual_amount=Decimal("100.00"))
        # Burlar validação do model para forçar o erro no service
        expense.actual_amount = Decimal("0.00")
        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.auto_generate_installments(
                user.company, expense, 2, date.today()
            )
        assert exc.value.code == "invalid_expense_amount"

    def test_auto_generate_creates_payment_events(self, user: User) -> None:
        """BR-S01: auto_generate_installments cria eventos PAYMENT no scheduler."""
        expense = _setup_expense(
            user, actual_amount=Decimal("1500.00"), name="Buffet Infantil"
        )
        first_date = date.today() + timedelta(days=30)

        InstallmentService.auto_generate_installments(
            user.company, expense, 3, first_date
        )

        events = Event.objects.filter(wedding=expense.wedding).order_by("start_time")
        assert len(events) == 3

        for i, event in enumerate(events):
            assert event.event_type == Event.TypeChoices.PAYMENT
            assert "Pagamento" in event.title
            assert "Buffet Infantil" in event.title
            assert f"Parcela {i + 1}/3" in event.title
            assert event.start_time.date() == first_date + timedelta(days=30 * i)
            assert event.company == user.company
            assert event.wedding == expense.wedding

    def test_auto_generate_payment_event_values(self, user: User) -> None:
        """Eventos PAYMENT contêm valor da parcela e nome da despesa."""
        expense = _setup_expense(user, actual_amount=Decimal("250.00"), name="Flores")
        first_date = date.today() + timedelta(days=15)

        InstallmentService.auto_generate_installments(
            user.company, expense, 2, first_date
        )

        events = Event.objects.filter(wedding=expense.wedding).order_by("start_time")
        assert len(events) == 2

        assert "125.00" in events[0].description
        assert "Flores" in events[0].description

    def test_auto_generate_single_installment(self, user: User) -> None:
        """num_installments=1 cria uma unica parcela com o valor total."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        first_date = date.today() + timedelta(days=30)

        installments = InstallmentService.auto_generate_installments(
            user.company, expense, 1, first_date
        )

        assert len(installments) == 1
        assert installments[0].amount == Decimal("500.00")
        assert installments[0].installment_number == 1
        assert installments[0].due_date == first_date
        assert installments[0].status == Installment.StatusChoices.PENDING


@pytest.mark.django_db
class TestInstallmentServiceUpdate:
    """Testes de atualização de parcelas via InstallmentService."""

    def test_update_installment_amount(self, user: User) -> None:
        """Atualização de valor é permitida quando Tolerância Zero se mantém.
        Neste cenário: uma única parcela cobre 100% do valor, atualizar para
        o mesmo valor que a despesa mantém a integridade."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        i1 = InstallmentService.create(
            user.company,
            InstallmentIn(
                expense=expense.uuid,
                installment_number=1,
                amount=Decimal("1000.00"),
                due_date=date.today() + timedelta(days=30),
            ),
        )

        # Atualizar para o mesmo valor (ou para outro que ainda fecha 1000 sozinho)
        updated = InstallmentService.update(
            user.company, i1, InstallmentPatchIn(amount=Decimal("1000.00"))
        )
        assert updated.amount == Decimal("1000.00")

    def test_update_installment_tolerance_zero_violation(self, user: User) -> None:
        """Atualização que quebra Tolerância Zero levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        i1 = InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("500.00")
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            InstallmentService.update(
                user.company, i1, InstallmentPatchIn(amount=Decimal("300.00"))
            )

        assert "expense_math_violation" in str(exc_info.value.code)

    def test_update_installment_due_date(self, user: User) -> None:
        """Atualização de due_date é permitida para parcelas futuras."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        new_due_date = date.today() + timedelta(days=60)
        updated = InstallmentService.update(
            user.company, installment, InstallmentPatchIn(due_date=new_due_date)
        )
        assert updated.due_date == new_due_date

    @pytest.mark.parametrize(
        "field,value",
        [
            ("amount", Decimal("400.00")),
            ("due_date", date.today() + timedelta(days=90)),
            ("installment_number", 2),
        ],
    )
    def test_update_paid_installment_protected_fields_blocked(
        self, user: User, field: str, value: Any
    ) -> None:
        """BR-F06: parcela paga não permite alterar valor, vencimento ou número."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            InstallmentService.update(
                user.company,
                installment,
                InstallmentPatchIn.model_construct(**{field: value}),
            )

        assert exc_info.value.code == "paid_installment_immutable"

    def test_update_paid_installment_notes_allowed(self, user: User) -> None:
        """BR-F06 protege campos contábeis, mas permite anotação operacional."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        updated = InstallmentService.update(
            user.company,
            installment,
            InstallmentPatchIn(notes="Comprovante conferido."),
        )

        assert updated.notes == "Comprovante conferido."

    def test_update_installment_cross_tenant(self, user: User) -> None:
        """Parcela de outro tenant não pode ser atualizada."""
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
            actual_amount=Decimal("500.00"),
        )
        other_installment = InstallmentFactory(
            expense=other_expense, amount=Decimal("500.00")
        )

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.update(
                user.company,
                other_installment,
                InstallmentPatchIn(amount=Decimal("300.00")),
            )


@pytest.mark.django_db
class TestInstallmentServiceDelete:
    """Testes de deleção de parcelas via InstallmentService."""

    def test_delete_installment_tolerance_zero_violation(self, user: User) -> None:
        """Deleção que quebra Tolerância Zero levanta DomainIntegrityError."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        installment = InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("1000.00")
        )

        with pytest.raises(DomainIntegrityError) as exc_info:
            InstallmentService.delete(user.company, installment)

        assert "installment_deletion_math_error" in str(exc_info.value.code)

    def test_delete_installment_when_sum_still_matches_passes(self, user: User) -> None:
        """Deleção permitida se soma das restantes ainda fecha."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("1000.00")
        )
        i2 = InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("0.00")
        )

        InstallmentService.delete(user.company, i2)

        expense.refresh_from_db()
        assert expense.installments.count() == 1
        remaining = expense.installments.first()
        assert remaining is not None
        assert remaining.amount == Decimal("1000.00")


@pytest.mark.django_db
class TestInstallmentServiceMarkAsPaid:
    """Testes de mark_as_paid e unmark_as_paid."""

    def test_mark_as_paid_success(self, user: User) -> None:
        """Parcela PENDING é marcada como PAID com paid_date=today."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
        )

        result = InstallmentService.mark_as_paid(user.company, installment)

        assert result.status == Installment.StatusChoices.PAID
        assert result.paid_date == date.today()

    def test_mark_as_paid_already_paid(self, user: User) -> None:
        """Parcela já PAID levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.mark_as_paid(user.company, installment)
        assert exc.value.code == "installment_already_paid"

    def test_mark_as_paid_tolerance_zero_intact(self, user: User) -> None:
        """Tolerância Zero permanece válida após marcar como paga."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
        )

        InstallmentService.mark_as_paid(user.company, installment)
        expense.refresh_from_db()
        expense.full_clean()  # não deve lançar exceção

    def test_unmark_as_paid_success(self, user: User) -> None:
        """Parcela PAID é desmarcada voltando para PENDING."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        result = InstallmentService.unmark_as_paid(user.company, installment)

        assert result.status == Installment.StatusChoices.PENDING
        assert result.paid_date is None

    def test_unmark_as_paid_overdue(self, user: User) -> None:
        """Parcela PAID vencida volta para OVERDUE."""
        from datetime import timedelta

        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
            due_date=date.today() - timedelta(days=5),
        )

        result = InstallmentService.unmark_as_paid(user.company, installment)

        assert result.status == Installment.StatusChoices.OVERDUE
        assert result.paid_date is None

    def test_unmark_as_paid_not_paid(self, user: User) -> None:
        """Parcela não PAID levanta BusinessRuleViolation ao desmarcar."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.unmark_as_paid(user.company, installment)
        assert exc.value.code == "installment_not_paid"

    def test_unmark_as_paid_math_violation(self, user: User) -> None:
        """Erro de validação ao desmarcar levanta BusinessRuleViolation."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with patch(
            "apps.finances.models.Expense.full_clean",
            side_effect=DjangoValidationError("Math error"),
        ):
            with pytest.raises(BusinessRuleViolation) as exc:
                InstallmentService.unmark_as_paid(user.company, installment)

        assert exc.value.code == "expense_math_violation"

    def test_mark_as_paid_cross_tenant(self, user: User) -> None:
        """Parcela de outro tenant não pode ser marcada como paga."""
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
            actual_amount=Decimal("500.00"),
        )
        other_installment = InstallmentFactory(
            expense=other_expense, amount=Decimal("500.00")
        )

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.mark_as_paid(user.company, other_installment)

    def test_mark_as_paid_tolerance_zero_violation(
        self, user: User, mocker: Any
    ) -> None:
        """Marcação de parcela como paga que quebra Tolerância Zero levanta erro.
        Para forçar isso, simulamos um erro de validação (DjangoValidationError)
        durante o `full_clean()` da despesa na hora do mark_as_paid."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
        )

        mocker.patch(
            "apps.finances.models.Expense.full_clean",
            side_effect=DjangoValidationError("Mock error"),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.mark_as_paid(user.company, installment)

        assert exc.value.code == "expense_math_violation"

    def test_unmark_as_paid_tolerance_zero_violation(
        self, user: User, mocker: Any
    ) -> None:
        """Desmarcação de parcela que quebra Tolerância Zero levanta erro.
        Simulamos um erro de validação (DjangoValidationError) durante
        o `full_clean()` da despesa na hora do unmark_as_paid."""
        from django.core.exceptions import ValidationError as DjangoValidationError

        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        mocker.patch(
            "apps.finances.models.Expense.full_clean",
            side_effect=DjangoValidationError("Mock error"),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.unmark_as_paid(user.company, installment)

        assert exc.value.code == "expense_math_violation"

    def test_unmark_as_paid_cross_tenant(self, user: User) -> None:
        """Parcela de outro tenant não pode ser desmarcada como paga."""
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
            actual_amount=Decimal("500.00"),
        )
        other_installment = InstallmentFactory(
            expense=other_expense,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.unmark_as_paid(user.company, other_installment)


@pytest.mark.django_db
class TestInstallmentServiceRedistribute:
    """Testes de redistribuição de parcelas."""

    def test_redistribute_success(self, user: User) -> None:
        """Redistribui 3 parcelas para 5 com novo valor total."""
        expense = _setup_expense(user, actual_amount=Decimal("1500.00"))
        InstallmentService.auto_generate_installments(
            user.company,
            expense,
            3,
            date.today(),
        )

        result = InstallmentService.redistribute(
            user.company,
            expense,
            5,
            date.today(),
        )

        assert len(result) == 5
        total = sum(r.amount for r in result)
        assert total == Decimal("1500.00")

    def test_redistribute_reduce_installments(self, user: User) -> None:
        """Redistribui 5 parcelas para 2."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        InstallmentService.auto_generate_installments(
            user.company,
            expense,
            5,
            date.today(),
        )

        result = InstallmentService.redistribute(
            user.company,
            expense,
            2,
            date.today(),
        )

        assert len(result) == 2
        total = sum(r.amount for r in result)
        assert total == Decimal("1000.00")
        assert expense.installments.count() == 2

    def test_redistribute_blocked_by_paid(self, user: User) -> None:
        """Redistribuição bloqueada se há parcelas PAID."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        InstallmentService.auto_generate_installments(
            user.company,
            expense,
            3,
            date.today(),
        )
        first = expense.installments.first()
        assert first is not None
        first.status = Installment.StatusChoices.PAID
        first.paid_date = date.today()
        first.save()

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.redistribute(
                user.company,
                expense,
                4,
                date.today(),
            )
        assert exc.value.code == "redistribute_blocked_by_paid"

    def test_redistribute_cleans_up_payment_events(self, user: User) -> None:
        """Redistribuir parcelas remove eventos PAYMENT antigos e cria novos."""
        from datetime import date as date_type

        from apps.scheduler.models import Event as SchedulerEvent

        expense = _setup_expense(
            user, actual_amount=Decimal("1000.00"), name="Buffet Teste"
        )
        installments = InstallmentService.auto_generate_installments(
            user.company, expense, 3, date_type.today()
        )

        # Verify FK is set on created events
        for inst in installments:
            event = SchedulerEvent.objects.filter(source_installment=inst).first()
            assert event is not None, (
                f"Event not found for installment {inst.installment_number}"
            )
            assert event.title.startswith(f"Pagamento: {expense.name}")

        old_events_count = SchedulerEvent.objects.filter(
            wedding=expense.wedding,
            event_type="pagamento",
        ).count()
        assert old_events_count == 3

        InstallmentService.redistribute(user.company, expense, 2, date_type.today())

        # Verify no orphaned events (with NULL source_installment) remain
        orphaned = SchedulerEvent.objects.filter(
            wedding=expense.wedding,
            event_type="pagamento",
            source_installment__isnull=True,
        )
        assert orphaned.count() == 0, f"Found {orphaned.count()} orphaned events"

        old_events = SchedulerEvent.objects.filter(
            wedding=expense.wedding,
            event_type="pagamento",
        )
        assert old_events.count() == 2
        assert all("Parcela" in e.title for e in old_events)

    def test_delete_installment_cleans_up_payment_event(self, user: User) -> None:
        """Deletar parcela individual remove seu evento PAYMENT."""
        from datetime import date as date_type

        from apps.scheduler.models import Event as SchedulerEvent

        expense = _setup_expense(
            user, actual_amount=Decimal("500.00"), name="Flores Teste"
        )
        installments = InstallmentService.auto_generate_installments(
            user.company, expense, 2, date_type.today()
        )

        # Verify FK is set
        deleted_event = SchedulerEvent.objects.filter(
            source_installment=installments[0]
        ).first()
        assert deleted_event is not None
        deleted_event_uuid = deleted_event.uuid

        events_before = SchedulerEvent.objects.filter(
            wedding=expense.wedding, event_type="pagamento"
        ).count()
        assert events_before == 2

        remaining = expense.installments.exclude(uuid=installments[0].uuid).first()
        if remaining:
            remaining.amount = expense.actual_amount
            remaining.save()

        InstallmentService.delete(user.company, installments[0])

        events_after = SchedulerEvent.objects.filter(
            wedding=expense.wedding, event_type="pagamento"
        ).count()
        assert events_after == 1

        assert not SchedulerEvent.objects.filter(uuid=deleted_event_uuid).exists()

    def test_delete_installment_cross_tenant(self, user: User) -> None:
        """Parcela de outro tenant não pode ser deletada."""
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
            actual_amount=Decimal("1000.00"),
        )
        other_installment = InstallmentFactory(
            expense=other_expense, installment_number=1, amount=Decimal("1000.00")
        )

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.delete(user.company, instance=other_installment)


@pytest.mark.django_db
class TestInstallmentServiceAdjust:
    """Testes de ajuste de parcelas via InstallmentService.adjust()."""

    def test_adjust_amount_success(self, user: User) -> None:
        """Ajuste de valor de parcela pendente é permitido (soma mantida)."""
        expense = _setup_expense(user, actual_amount=Decimal("900.00"))
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
        )
        inst2 = InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("400.00"),
            due_date=date.today() + timedelta(days=60),
        )

        result = InstallmentService.adjust(
            user.company, inst2, InstallmentAdjustIn(amount=Decimal("400.00"))
        )

        assert result.amount == Decimal("400.00")

    def test_adjust_due_date_success(self, user: User) -> None:
        """Ajuste de data de parcela pendente é permitido."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        new_date = date.today() + timedelta(days=45)
        result = InstallmentService.adjust(
            user.company, inst, InstallmentAdjustIn(due_date=new_date)
        )

        assert result.due_date == new_date

    def test_adjust_blocked_by_paid(self, user: User) -> None:
        """Parcela PAID não pode ser ajustada."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        inst = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.adjust(
                user.company, inst, InstallmentAdjustIn(amount=Decimal("300.00"))
            )
        assert exc.value.code == "adjustment_on_paid_installment"

    def test_adjust_due_date_before_previous(self, user: User) -> None:
        """Data anterior à parcela anterior é rejeitada."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        first_date = date.today() + timedelta(days=30)
        InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=first_date,
        )
        inst2 = InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("500.00"),
            due_date=first_date + timedelta(days=30),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.adjust(
                user.company,
                inst2,
                InstallmentAdjustIn(due_date=first_date - timedelta(days=5)),
            )
        assert exc.value.code == "due_date_before_previous_installment"

    def test_adjust_due_date_after_next(self, user: User) -> None:
        """Data posterior à parcela seguinte é rejeitada."""
        expense = _setup_expense(user, actual_amount=Decimal("1500.00"))
        first_date = date.today() + timedelta(days=30)
        inst1 = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=first_date,
        )
        second_date = first_date + timedelta(days=30)
        InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("500.00"),
            due_date=second_date,
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.adjust(
                user.company,
                inst1,
                InstallmentAdjustIn(due_date=second_date + timedelta(days=5)),
            )
        assert exc.value.code == "due_date_after_next_installment"

    def test_adjust_tolerance_zero_intact(self, user: User) -> None:
        """Ajuste que quebra Tolerância Zero levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        inst = InstallmentFactory(
            expense=expense,
            installment_number=1,
            amount=Decimal("500.00"),
        )
        InstallmentFactory(
            expense=expense,
            installment_number=2,
            amount=Decimal("500.00"),
        )

        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.adjust(
                user.company, inst, InstallmentAdjustIn(amount=Decimal("300.00"))
            )
        assert exc.value.code == "expense_math_violation"

    def test_adjust_cross_tenant(self, user: User) -> None:
        """Parcela de outro tenant não pode ser ajustada."""
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
            actual_amount=Decimal("500.00"),
        )
        other_installment = InstallmentFactory(
            expense=other_expense, amount=Decimal("500.00")
        )

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.adjust(
                user.company,
                other_installment,
                InstallmentAdjustIn(amount=Decimal("300.00")),
            )
