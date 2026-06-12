from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import BudgetCategory
from apps.finances.models.installment import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestBudgetCategoryModelMetadata:
    """Testes de representação e metadados do modelo BudgetCategory."""

    def test_budget_category_str_representation(self, user):
        """__str__ deve conter o nome e o wedding."""
        wedding = WeddingFactory(
            user_context=user, bride_name="Ana", groom_name="Pedro"
        )
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            name="Decoração",
            allocated_budget=Decimal("5000.00"),
        )

        result = str(category)
        assert "Decoração" in result
        assert "Ana" in result

    def test_budget_category_ordering_by_name(self, user):
        """Ordenação padrão deve ser por name alfabético."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)

        BudgetCategoryFactory(budget=budget, wedding=wedding, name="Zeta")
        BudgetCategoryFactory(budget=budget, wedding=wedding, name="Alfa")
        BudgetCategoryFactory(budget=budget, wedding=wedding, name="Beta")

        categories = list(BudgetCategory.objects.filter(budget=budget))
        assert categories[0].name == "Alfa"
        assert categories[1].name == "Beta"
        assert categories[2].name == "Zeta"

    def test_budget_category_unique_name_per_budget(self, user):
        """Nome deve ser único dentro do mesmo budget."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)

        BudgetCategoryFactory(budget=budget, wedding=wedding, name="Decoração")

        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError):
            BudgetCategoryFactory(budget=budget, wedding=wedding, name="Decoração")

    def test_budget_category_allocated_budget_not_negative(self, user):
        """allocated_budget não pode ser negativo."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategory(
            company=user.company,
            budget=budget,
            wedding=wedding,
            name="Teste",
            allocated_budget=Decimal("-1.00"),
        )

        with pytest.raises(ValidationError):
            category.full_clean()


@pytest.mark.django_db
class TestBudgetCategoryClean:
    """Testes das validações do método clean()."""

    def test_clean_fails_when_budget_wedding_mismatch(self, user):
        """TRAVA: orçamento pai deve pertencer ao mesmo casamento da categoria.
        O WeddingOwnedMixin captura essa violação antes do clean() customizado."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        budget1 = BudgetFactory(wedding=wedding1)

        category = BudgetCategory(
            company=user.company,
            budget=budget1,
            wedding=wedding2,
            name="Cross-Wedding",
            allocated_budget=Decimal("1000.00"),
        )

        with pytest.raises(ValidationError) as exc_info:
            category.full_clean()

        assert "outro casamento" in str(exc_info.value).lower()


@pytest.mark.django_db
class TestBudgetCategoryTotalSpent:
    """Testes da computed property total_spent."""

    def test_total_spent_with_no_expenses(self, user):
        """Sem despesas, total_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        assert category.total_spent == Decimal("0.00")

    def test_total_spent_sums_expenses(self, user):
        """total_spent soma apenas parcelas PAID das despesas."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense1 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("1500.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense1,
            amount=Decimal("1500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )

        expense2 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("3500.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense2,
            amount=Decimal("3500.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )

        assert category.total_spent == Decimal("5000.00")

    def test_total_spent_only_paid_installments(self, user):
        """total_spent soma apenas parcelas PAID, ignorando PENDING."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("6000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("3000.00")

    def test_total_spent_all_pending_returns_zero(self, user):
        """Todas as parcelas PENDING: total_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("4000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("4000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("0.00")

    def test_total_spent_multiple_expenses_mixed_status(self, user):
        """Soma PAID de múltiplas despesas, ignorando PENDING em todas."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        exp1 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("3000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=exp1,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )

        exp2 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("2000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=exp2,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-02-15",
        )
        InstallmentFactory(
            expense=exp2,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("4000.00")
