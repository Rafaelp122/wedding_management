from decimal import Decimal

import pytest
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
from apps.tenants.models import Company
from apps.weddings.services.summaries.financial import FinancialSummaryService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestBoltOptimizations:
    def setup_method(self):
        self.company = Company.objects.create(name="Bolt Co", slug="bolt-co")
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
            paid_date=timezone.now().date(),
        )

    def test_budget_total_overall_spent_annotated(self):
        """Tests that the property uses the annotated value if available."""
        budget = Budget.objects.with_total_spent().get(uuid=self.budget.uuid)
        assert hasattr(budget, "_total_overall_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = budget.total_overall_spent
            assert spent == Decimal("200.00")

        assert len(ctx) == 0, "Should NOT trigger a query when annotated"

    def test_budget_total_overall_spent_fallback(self):
        """Tests that the property falls back to a query if not annotated."""
        budget = Budget.objects.get(uuid=self.budget.uuid)
        assert not hasattr(budget, "_total_overall_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = budget.total_overall_spent
            assert spent == Decimal("200.00")

        assert len(ctx) == 1, "Should trigger a fallback query when NOT annotated"

    def test_category_total_spent_annotated(self):
        """Tests that the property uses the annotated value if available."""
        category = BudgetCategory.objects.with_total_spent().get(
            uuid=self.category.uuid
        )
        assert hasattr(category, "_total_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = category.total_spent
            assert spent == Decimal("200.00")

        assert len(ctx) == 0, "Should NOT trigger a query when annotated"

    def test_category_total_spent_fallback(self):
        """Tests that the property falls back to a query if not annotated."""
        category = BudgetCategory.objects.get(uuid=self.category.uuid)
        assert not hasattr(category, "_total_spent")

        with CaptureQueriesContext(connection) as ctx:
            spent = category.total_spent
            assert spent == Decimal("200.00")

        assert len(ctx) == 1, "Should trigger a fallback query when NOT annotated"

    def test_budget_percentage_used_optimized(self):
        """Tests that the service uses the optimized path (1 query)."""
        with CaptureQueriesContext(connection) as ctx:
            pct = FinancialSummaryService.budget_percentage_used(
                company=self.company, wedding=self.wedding
            )
            assert pct == 20.0

        assert len(ctx) == 1, f"Expected 1 query, got {len(ctx)}"

    def test_budget_percentage_used_no_budget(self):
        """Tests the percentage when no budget exists."""
        wedding_no_budget = WeddingFactory(company=self.company)
        pct = FinancialSummaryService.budget_percentage_used(
            company=self.company, wedding=wedding_no_budget
        )
        assert pct == 0.0

    def test_budget_percentage_used_zero_estimated(self):
        """Tests the percentage when estimated budget is zero."""
        budget_zero = BudgetFactory(
            wedding=WeddingFactory(company=self.company),
            company=self.company,
            total_estimated=Decimal("0.00"),
        )
        pct = FinancialSummaryService.budget_percentage_used(
            company=self.company, wedding=budget_zero.wedding
        )
        assert pct == 0.0

    def test_expense_with_details_manager(self):
        """Tests the new manager proxy method for with_details."""
        with CaptureQueriesContext(connection) as ctx:
            expenses = list(Expense.objects.with_details())
            assert len(expenses) >= 1
            e = expenses[0]
            # Accessing annotated fields shouldn't trigger new queries
            assert e.installments_count >= 1
            assert e.paid_installments_count == 1
            assert e.total_paid == Decimal("200.00")

        assert len(ctx) == 1, f"Expected 1 query, got {len(ctx)}"

    def test_pending_installments_7d(self):
        """Tests pending installments in the next 7 days."""
        # Due in 5 days
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("150.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=timezone.now().date() + timezone.timedelta(days=5),
        )
        # Due in 10 days (should be ignored)
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("300.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=timezone.now().date() + timezone.timedelta(days=10),
        )

        total = FinancialSummaryService.pending_installments_7d(company=self.company)
        assert total == Decimal("150.00")

    def test_overdue_installments(self):
        """Tests overdue installments logic."""
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
            due_date=timezone.now().date() - timezone.timedelta(days=1),
        )

        amount, count = FinancialSummaryService.overdue_installments(
            company=self.company
        )
        assert amount == Decimal("120.00")
        assert count == 2

    def test_upcoming_installments(self):
        """Tests upcoming installments for a wedding."""
        # We created one PAID in setup_method (ignored)
        # Let's add more.
        InstallmentFactory(
            expense=self.expense,
            wedding=self.wedding,
            company=self.company,
            amount=Decimal("10.00"),
            status=Installment.StatusChoices.PENDING,
            due_date=timezone.now().date() + timezone.timedelta(days=1),
        )

        results = FinancialSummaryService.upcoming_installments(
            company=self.company, wedding=self.wedding
        )
        assert len(results) >= 1
        assert any(r["amount"] == "10.00" for r in results)

    def test_categories_summary(self):
        """Tests the categories summary for a wedding."""
        summary = FinancialSummaryService.categories_summary(
            company=self.company, wedding=self.wedding
        )
        assert len(summary) >= 1
        assert summary[0]["name"] == self.category.name
        assert float(summary[0]["spent"]) == 200.0

    def test_budget_category_clean_validation(self):
        """Tests the safety check for cross-wedding budget categories."""
        other_wedding = WeddingFactory(company=self.company)
        # Ensure we are comparing different weddings
        assert self.budget.wedding_id != other_wedding.id
        self.category.wedding = other_wedding
        from django.core.exceptions import ValidationError

        with pytest.raises(ValidationError) as excinfo:
            self.category.clean()
        assert "Este recurso pertence a outro casamento" in str(excinfo.value)
