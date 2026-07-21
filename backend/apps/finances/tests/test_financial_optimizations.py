from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.services.summaries.financial import FinancialSummaryService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestFinancialOptimizations:
    def setup_method(self) -> None:
        self.company = CompanyFactory(name="Empresa Teste", slug="empresa-teste")
        self.wedding = WeddingFactory(company=self.company)
        self.budget = BudgetFactory(
            wedding=self.wedding,
            company=self.company,
            total_estimated=Decimal("1000.00"),
        )
        self.category = BudgetCategoryFactory(
            budget=self.budget,
            wedding=self.wedding,
            company=self.company,
            allocated_budget=Decimal("500.00"),
        )
        self.expense = ExpenseFactory(
            category=self.category,
            wedding=self.wedding,
            company=self.company,
            actual_amount=Decimal("200.00"),
        )

        # Create 1 paid installment
        self.installment = InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("200.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=timezone.localdate(),
        )

    def test_budget_total_overall_spent_annotated(self) -> None:
        """Tests that the property uses the annotated value if available."""
        budget = Budget.objects.with_total_spent().get(uuid=self.budget.uuid)
        assert hasattr(budget, "_total_overall_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = budget.total_overall_spent
            assert spent == Decimal("200.00")
            assert len(ctx) == 0

    def test_budget_total_overall_spent_fallback(self) -> None:
        """Tests fallback query when annotated attribute is absent."""
        budget = Budget.objects.get(uuid=self.budget.uuid)
        assert not hasattr(budget, "_total_overall_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = budget.total_overall_spent
            assert spent == Decimal("200.00")
            assert len(ctx) == 1

    def test_budget_category_total_spent_annotated(self) -> None:
        """Tests that category property uses annotated value if available."""
        category = BudgetCategory.objects.with_total_spent().get(
            uuid=self.category.uuid
        )
        assert hasattr(category, "_total_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = category.total_spent
            assert spent == Decimal("200.00")
            assert len(ctx) == 0

    def test_budget_category_total_spent_fallback(self) -> None:
        """Tests fallback query for category when annotated attribute is absent."""
        category = BudgetCategory.objects.get(uuid=self.category.uuid)
        assert not hasattr(category, "_total_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = category.total_spent
            assert spent == Decimal("200.00")
            assert len(ctx) == 1

    def test_budget_percentage_used_performance(self) -> None:
        """Tests that budget_percentage_used only performs 1 query."""
        with CaptureQueriesContext(connection) as ctx:
            pct = FinancialSummaryService.budget_percentage_used(
                company=self.company, wedding=self.wedding
            )
            assert pct == 20.0
            assert len(ctx) == 1

    def test_budget_percentage_used_without_budget(self) -> None:
        """Tests budget_percentage_used returns 0.0 when wedding has no budget."""
        other_wedding = WeddingFactory(company=self.company)
        pct = FinancialSummaryService.budget_percentage_used(
            company=self.company, wedding=other_wedding
        )
        assert pct == 0.0

    def test_expense_with_details_annotation(self) -> None:
        """Tests that ExpenseQuerySet.with_details annotates required fields."""
        expense = Expense.objects.with_details().get(uuid=self.expense.uuid)
        assert hasattr(expense, "installments_count")
        assert hasattr(expense, "paid_installments_count")
        assert hasattr(expense, "total_paid")
        assert hasattr(expense, "total_pending")

        assert expense.installments_count == 1
        assert expense.paid_installments_count == 1
        assert expense.total_paid == Decimal("200.00")
        assert expense.total_pending == Decimal("0.00")

    def test_pending_installments_7d(self) -> None:
        """Tests pending installments due in next 7 days."""
        today = timezone.localdate()
        # Due in 3 days
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("150.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=today + timezone.timedelta(days=3),
        )
        # Due in 10 days (should be ignored)
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("300.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=today + timezone.timedelta(days=10),
        )

        total = FinancialSummaryService.pending_installments_7d(
            company=self.company, today=today
        )
        assert total == Decimal("150.00")

    def test_pending_installments_7d_empty(self) -> None:
        """Tests pending installments returns Decimal 0.00 when empty."""
        other_company = CompanyFactory()
        total = FinancialSummaryService.pending_installments_7d(company=other_company)
        assert total == Decimal("0.00")

    def test_overdue_installments(self) -> None:
        """Tests overdue installments logic."""
        today = timezone.localdate()
        # Explicitly OVERDUE
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("50.00"),
            status=Installment.StatusChoices.OVERDUE,
        )
        # PENDING but past due date
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("70.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=today - timezone.timedelta(days=1),
        )

        amount, count = FinancialSummaryService.overdue_installments(
            company=self.company, today=today
        )
        assert amount == Decimal("120.00")
        assert count == 2

    def test_overdue_installments_empty(self) -> None:
        """Tests overdue installments returns (0.00, 0) when empty."""
        other_company = CompanyFactory()
        amount, count = FinancialSummaryService.overdue_installments(
            company=other_company
        )
        assert amount == Decimal("0.00")
        assert count == 0

    def test_upcoming_installments(self) -> None:
        """Tests upcoming installments for a wedding."""
        today = timezone.localdate()
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("10.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=today + timezone.timedelta(days=1),
        )

        results = FinancialSummaryService.upcoming_installments(
            company=self.company, wedding=self.wedding, today=today
        )
        assert len(results) >= 1
        assert any(r["amount"] == "10.00" for r in results)

    def test_upcoming_installments_empty(self) -> None:
        """Tests upcoming_installments returns empty list when empty."""
        other_wedding = WeddingFactory(company=self.company)
        results = FinancialSummaryService.upcoming_installments(
            company=self.company, wedding=other_wedding
        )
        assert results == []

    def test_categories_summary(self) -> None:
        """Tests the categories summary for a wedding."""
        summary = FinancialSummaryService.categories_summary(
            company=self.company, wedding=self.wedding
        )
        assert len(summary) >= 1
        assert summary[0]["name"] == self.category.name
        assert float(summary[0]["spent"]) == 200.0

    def test_categories_summary_empty(self) -> None:
        """Tests categories_summary returns empty list when empty."""
        other_wedding = WeddingFactory(company=self.company)
        summary = FinancialSummaryService.categories_summary(
            company=self.company, wedding=other_wedding
        )
        assert summary == []

    def test_budget_category_clean_validation(self) -> None:
        """Tests the safety check for cross-wedding budget categories."""
        other_wedding = WeddingFactory(company=self.company)
        assert self.budget.wedding_id != other_wedding.id
        self.category.wedding = other_wedding

        with pytest.raises(ValidationError) as excinfo:
            self.category.clean()
        assert "Este recurso pertence a outro casamento" in str(excinfo.value)
