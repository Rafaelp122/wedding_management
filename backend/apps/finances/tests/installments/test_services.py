from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Installment
from apps.finances.services.installment_service import InstallmentService
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_expense(user, **kwargs):
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

    def test_create_installment_success(self, user):
        """Criação de parcela com valor compatível com a despesa."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))

        data = {
            "expense": expense.uuid,
            "installment_number": 1,
            "amount": Decimal("1000.00"),
            "due_date": date.today() + timedelta(days=30),
        }

        installment = InstallmentService.create(user.company, data)

        assert installment.expense == expense
        assert installment.installment_number == 1
        assert installment.amount == Decimal("1000.00")
        assert installment.status == Installment.StatusChoices.PENDING

    def test_create_installment_with_expense_instance(self, user):
        """create() aceita instância de Expense, não só UUID."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))

        data = {
            "expense": expense,
            "installment_number": 1,
            "amount": Decimal("500.00"),
            "due_date": date.today() + timedelta(days=15),
        }

        installment = InstallmentService.create(user.company, data)
        assert installment.expense == expense

    def test_create_installment_tolerance_zero_violation(self, user):
        """Tolerância Zero: soma != actual_amount levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))

        data = {
            "expense": expense.uuid,
            "installment_number": 1,
            "amount": Decimal("999.99"),
            "due_date": date.today() + timedelta(days=30),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            InstallmentService.create(user.company, data)

        assert "expense_math_violation" in str(exc_info.value.code)

    def test_create_installment_exact_sum_passes(self, user):
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

    def test_create_installment_expense_not_found(self, user):
        """UUID de despesa inexistente deve levantar ObjectNotFoundError."""
        data = {
            "expense": uuid4(),
            "installment_number": 1,
            "amount": Decimal("100.00"),
            "due_date": date.today() + timedelta(days=10),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            InstallmentService.create(user.company, data)

        assert "expense_not_found_or_denied" in str(exc_info.value.code)

    def test_create_installment_multitenancy_isolation(self):
        """Usuário A não pode criar parcela em despesa do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        expense_b = _setup_expense(user_b, actual_amount=Decimal("500.00"))

        data = {
            "expense": expense_b.uuid,
            "installment_number": 1,
            "amount": Decimal("500.00"),
            "due_date": date.today() + timedelta(days=30),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            InstallmentService.create(user_a.company, data)

        assert "expense_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestInstallmentServiceAutoGeneration:
    """Testes de geração automática de parcelas."""

    def test_auto_generate_invalid_num_installments(self, user):
        expense = _setup_expense(user, actual_amount=Decimal("100.00"))
        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.auto_generate_installments(
                user.company, expense, 0, date.today()
            )
        assert exc.value.code == "invalid_installment_number"

    def test_auto_generate_invalid_expense_amount(self, user):
        expense = _setup_expense(user, actual_amount=Decimal("0.00"))
        # Burlar validação do model para forçar o erro no service
        expense.actual_amount = Decimal("0.00")
        with pytest.raises(BusinessRuleViolation) as exc:
            InstallmentService.auto_generate_installments(
                user.company, expense, 2, date.today()
            )
        assert exc.value.code == "invalid_expense_amount"


@pytest.mark.django_db
class TestInstallmentServiceUpdate:
    """Testes de atualização de parcelas via InstallmentService."""

    def test_update_installment_amount(self, user):
        """Atualização de valor é permitida quando Tolerância Zero se mantém.
        Neste cenário: uma única parcela cobre 100% do valor, atualizar para
        o mesmo valor que a despesa mantém a integridade."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        i1 = InstallmentService.create(
            user.company,
            {
                "expense": expense,
                "installment_number": 1,
                "amount": Decimal("1000.00"),
                "due_date": date.today() + timedelta(days=30),
            },
        )

        # Atualizar para o mesmo valor (ou para outro que ainda fecha 1000 sozinho)
        updated = InstallmentService.update(
            user.company, i1, {"amount": Decimal("1000.00")}
        )
        assert updated.amount == Decimal("1000.00")

    def test_update_installment_tolerance_zero_violation(self, user):
        """Atualização que quebra Tolerância Zero levanta BusinessRuleViolation."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        i1 = InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("500.00")
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            InstallmentService.update(user.company, i1, {"amount": Decimal("300.00")})

        assert "expense_math_violation" in str(exc_info.value.code)

    def test_update_installment_cannot_change_expense(self, user):
        """Campos estruturais (expense, wedding, company) são bloqueados."""
        expense1 = _setup_expense(user, actual_amount=Decimal("500.00"))
        expense2 = _setup_expense(user, actual_amount=Decimal("500.00"))
        i1 = InstallmentFactory(expense=expense1, amount=Decimal("500.00"))
        InstallmentFactory(expense=expense2, amount=Decimal("500.00"))

        updated = InstallmentService.update(
            user.company, i1, {"expense": expense2.uuid}
        )
        assert updated.expense == expense1

    def test_update_installment_due_date(self, user):
        """Atualização de due_date é permitida para parcelas futuras."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(
            expense=expense,
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=30),
        )

        new_due_date = date.today() + timedelta(days=60)
        updated = InstallmentService.update(
            user.company, installment, {"due_date": new_due_date}
        )
        assert updated.due_date == new_due_date


@pytest.mark.django_db
class TestInstallmentServiceDelete:
    """Testes de deleção de parcelas via InstallmentService."""

    def test_delete_installment_tolerance_zero_violation(self, user):
        """Deleção que quebra Tolerância Zero levanta DomainIntegrityError."""
        expense = _setup_expense(user, actual_amount=Decimal("1000.00"))
        installment = InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("1000.00")
        )

        with pytest.raises(DomainIntegrityError) as exc_info:
            InstallmentService.delete(user.company, installment)

        assert "installment_deletion_math_error" in str(exc_info.value.code)

    def test_delete_installment_when_sum_still_matches_passes(self, user):
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
        assert expense.installments.first().amount == Decimal("1000.00")


@pytest.mark.django_db
class TestInstallmentServiceListAndGet:
    """Testes de listagem e obtenção de parcelas."""

    def test_list_installments_multitenancy(self):
        """list() retorna apenas parcelas do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        expense_a = _setup_expense(user_a)
        expense_b = _setup_expense(user_b)

        InstallmentFactory(expense=expense_a, amount=Decimal("500.00"))
        InstallmentFactory(expense=expense_b, amount=Decimal("300.00"))

        qs_a = InstallmentService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().expense.company == user_a.company

        qs_b = InstallmentService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().expense.company == user_b.company

    def test_get_installment_success(self, user):
        """get() retorna parcela por UUID com select_related."""
        expense = _setup_expense(user, actual_amount=Decimal("500.00"))
        installment = InstallmentFactory(expense=expense, amount=Decimal("500.00"))

        result = InstallmentService.get(user.company, installment.uuid)
        assert result.uuid == installment.uuid
        assert result.expense == expense

    def test_get_installment_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            InstallmentService.get(user.company, uuid4())

    def test_get_installment_multitenancy(self):
        """Usuário A não pode acessar parcela do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        expense_b = _setup_expense(user_b)
        installment_b = InstallmentFactory(expense=expense_b)

        with pytest.raises(ObjectNotFoundError):
            InstallmentService.get(user_a.company, installment_b.uuid)
