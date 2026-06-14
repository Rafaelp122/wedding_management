"""
Testes para o comando seed_db.

Verifica se o comando popula o banco corretamente com dados de
desenvolvimento: planners, casamentos, contratos, despesas, parcelas,
tarefas e eventos.
"""

import pytest
from django.core.management import call_command

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.logistics.models import Contract, Item, Supplier
from apps.scheduler.models import Event, Task
from apps.users.models import User
from apps.weddings.models import Wedding


@pytest.mark.django_db
class TestSeedDbCommand:
    def test_seed_db_creates_superuser(self):
        call_command("seed_db", planners=0, weddings=0)

        assert User.objects.filter(is_superuser=True).exists()

    def test_seed_db_creates_planners(self):
        call_command("seed_db", planners=3, weddings=0)

        planners = User.objects.filter(is_superuser=False, is_staff=False)
        assert planners.count() >= 3

    def test_seed_db_creates_weddings_with_mixed_statuses(self):
        call_command("seed_db", planners=1, weddings=3)

        weddings = Wedding.objects.order_by("-created_at")[:3]
        assert weddings.count() == 3

        statuses = {w.status for w in weddings}
        assert Wedding.StatusChoices.COMPLETED in statuses
        assert Wedding.StatusChoices.IN_PROGRESS in statuses

    def test_seed_db_creates_suppliers_with_tenant_context(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        assert wedding is not None

        suppliers = Supplier.objects.filter(company=wedding.company)
        assert suppliers.count() >= 5

    def test_seed_db_creates_contracts_with_mixed_statuses(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        contracts = Contract.objects.filter(wedding=wedding)

        assert contracts.count() == 3

        statuses = {c.status for c in contracts}
        assert Contract.StatusChoices.SIGNED in statuses
        assert Contract.StatusChoices.DRAFT in statuses

    def test_seed_db_creates_items_for_contracts(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        items = Item.objects.filter(wedding=wedding)

        assert items.count() == 6

    def test_seed_db_creates_expenses_linked_to_contracts(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        expenses = Expense.objects.filter(wedding=wedding)

        assert expenses.count() == 3
        for expense in expenses:
            assert expense.contract is not None

    def test_seed_db_creates_installments_with_mixed_statuses(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        installments = Installment.objects.filter(wedding=wedding)

        assert installments.count() == 9

        statuses = {s for s in installments.values_list("status", flat=True)}
        assert Installment.StatusChoices.PAID in statuses
        assert Installment.StatusChoices.PENDING in statuses
        assert Installment.StatusChoices.OVERDUE in statuses

    def test_seed_db_creates_budget_and_categories(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        budgets = Budget.objects.filter(wedding=wedding)
        categories = BudgetCategory.objects.filter(wedding=wedding)

        assert budgets.count() == 1
        assert categories.count() == 3

    def test_seed_db_creates_tasks_with_mixed_completion(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        tasks = Task.objects.filter(wedding=wedding)

        assert tasks.count() == 5
        assert tasks.filter(is_completed=True).count() == 3
        assert tasks.filter(is_completed=False).count() == 2

    def test_seed_db_creates_calendar_events(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        events = Event.objects.filter(wedding=wedding)

        assert events.count() == 4

    def test_seed_db_generates_no_errors_on_default_run(self):
        call_command("seed_db")

        assert Wedding.objects.count() > 0
        assert User.objects.filter(is_superuser=True).exists()
