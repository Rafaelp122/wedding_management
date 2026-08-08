"""Testes para os comandos de seed (seed_db e seed_e2e).

Verifica se os comandos populam o banco corretamente e de forma
idempotente com dados de desenvolvimento e suíte E2E.
"""

from datetime import date, timedelta

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
        assert planners.count() == 4  # 3 batch + 1 E2E

    def test_seed_db_creates_weddings_with_mixed_statuses(self):
        call_command("seed_db", planners=1, weddings=3)

        weddings = Wedding.objects.order_by("-created_at")[:3]
        assert weddings.count() == 3

        statuses = {w.status for w in weddings}
        assert Wedding.StatusChoices.COMPLETED in statuses
        assert Wedding.StatusChoices.IN_PROGRESS in statuses

    @pytest.mark.parametrize("num_weddings", [1, 3])
    def test_seed_db_creates_critical_wedding_for_each_planner(self, num_weddings):
        call_command("seed_db", planners=1, weddings=num_weddings)

        planners = User.objects.filter(is_superuser=False, is_staff=False)
        for planner in planners:
            wedding = (
                Wedding.objects.filter(
                    company=planner.company,
                    status=Wedding.StatusChoices.IN_PROGRESS,
                )
                .order_by("created_at")
                .first()
            )
            assert wedding is not None
            assert date.today() <= wedding.date <= date.today() + timedelta(days=90)

    def test_seed_db_creates_suppliers_with_tenant_context(self):
        call_command("seed_db", planners=1, weddings=1)

        wedding = Wedding.objects.order_by("-created_at").first()
        assert wedding is not None

        suppliers = Supplier.objects.filter(company=wedding.company)
        assert suppliers.count() == 5

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

    def test_seed_db_creates_e2e_planner(self):
        call_command("seed_db", planners=0, weddings=0)

        e2e = User.objects.filter(email="planner@example.com").first()
        assert e2e is not None
        assert e2e.is_active is True
        assert e2e.is_staff is False
        assert e2e.is_superuser is False

    def test_seed_db_is_idempotent(self):
        call_command("seed_db", planners=1, weddings=1)
        call_command("seed_db", planners=1, weddings=1)

        e2e_planners = User.objects.filter(email="planner@example.com")
        assert e2e_planners.count() == 1

        superusers = User.objects.filter(is_superuser=True)
        assert superusers.count() == 1


@pytest.mark.django_db
class TestSeedE2ECommand:
    def test_seed_e2e_creates_expected_entities(self):
        call_command("seed_e2e")

        assert User.objects.filter(email="admin@admin.com", is_superuser=True).exists()
        planner = User.objects.filter(email="planner@example.com").first()
        assert planner is not None
        assert User.objects.filter(email="staff@example.com", is_staff=True).exists()

        weddings = Wedding.objects.filter(company=planner.company)
        assert weddings.count() == 2

        active_wedding = weddings.get(status=Wedding.StatusChoices.IN_PROGRESS)
        assert active_wedding.groom_name == "João"
        assert active_wedding.bride_name == "Maria"

        completed_wedding = weddings.get(status=Wedding.StatusChoices.COMPLETED)
        assert completed_wedding.groom_name == "Carlos"

        budget = Budget.objects.get(wedding=active_wedding)
        assert budget.categories.count() == 3

        contract = Contract.objects.get(wedding=active_wedding)
        assert contract.status == Contract.StatusChoices.SIGNED

        installments = Installment.objects.filter(wedding=active_wedding)
        assert installments.filter(status=Installment.StatusChoices.PAID).count() == 1
        assert (
            installments.filter(status=Installment.StatusChoices.OVERDUE).count() == 1
        )
        assert (
            installments.filter(status=Installment.StatusChoices.PENDING).count() == 1
        )

        tasks = Task.objects.filter(wedding=active_wedding)
        assert tasks.filter(is_completed=False).count() == 2

    def test_seed_e2e_is_idempotent(self):
        call_command("seed_e2e")
        call_command("seed_e2e")

        assert User.objects.filter(email="planner@example.com").count() == 1
        planner = User.objects.get(email="planner@example.com")
        company = planner.company

        assert Wedding.objects.filter(company=company).count() == 2
        assert Budget.objects.filter(company=company).count() == 1
        assert Contract.objects.filter(company=company).count() == 1
        assert Expense.objects.filter(company=company).count() == 1
        assert Installment.objects.filter(company=company).count() == 3
        assert Task.objects.filter(wedding__company=company).count() == 5
        assert Event.objects.filter(wedding__company=company).count() == 4
