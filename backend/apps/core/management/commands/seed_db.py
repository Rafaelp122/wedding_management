"""
Comando de seed para popular o banco com dados de desenvolvimento.

Cria planners, casamentos, fornecedores, contratos, despesas, parcelas,
tarefas e eventos com dados realistas para facilitar o desenvolvimento local.

Uso:
    python manage.py seed_db
    python manage.py seed_db --planners 3 --weddings 4
"""

import secrets
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.models import Contract
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.tests.factories import EventFactory, TaskFactory
from apps.users.tests.factories import AdminFactory, UserFactory
from apps.weddings.tests.factories import WeddingFactory


class Command(BaseCommand):
    help = (
        "Popula o banco com quantidades customizáveis de usuários, "
        "casamentos e dados reais"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--planners",
            type=int,
            default=2,
            help="Número de Planners (usuários) a serem criados",
        )
        parser.add_argument(
            "--weddings",
            type=int,
            default=2,
            help="Número de casamentos por cada Planner",
        )

    @transaction.atomic
    def handle(self, *args, **kwargs):
        num_planners = kwargs["planners"]
        num_weddings = kwargs["weddings"]

        self.stdout.write(
            self.style.MIGRATE_LABEL(
                f"Iniciando seed completo: {num_planners} planners com "
                f"{num_weddings} casamentos cada..."
            )
        )

        # 1. Superuser (only if none exists)
        if (
            not AdminFactory._get_manager(AdminFactory._meta.model)
            .filter(is_superuser=True)
            .exists()
        ):
            AdminFactory.create(
                email="admin@admin.com",
                first_name="Admin",
                last_name="Master",
            )
            self.stdout.write(
                self.style.SUCCESS("  ✓ Superusuário admin@admin.com criado")
            )

        # 2. Planners
        planners = UserFactory.create_batch(num_planners)
        self.stdout.write(self.style.SUCCESS(f"  ✓ {num_planners} planners criados"))

        for planner in planners:
            # Pool of 5 suppliers for this planner's company.
            # Override phone to avoid Faker generating values > max_length=20.
            suppliers = SupplierFactory.create_batch(
                5,
                company=planner.company,
                phone="(11) 99999-0000",
            )

            # 3. Weddings (mix of IN_PROGRESS and COMPLETED)
            for i in range(num_weddings):
                # Make the first wedding completed (when there are multiple).
                if i == 0 and num_weddings > 1:
                    # CompletedWeddingFactory uses past_date which fails the
                    # validate_future_date field validator (raises when date <
                    # today). Use timezone.now().date() (UTC) to match what the
                    # validator checks, avoiding local timezone offset issues.
                    # The model's clean() allows COMPLETED with today's date.
                    wedding = WeddingFactory.create(
                        user_context=planner,
                        date=timezone.now().date(),
                        status="COMPLETED",
                    )
                else:
                    wedding = WeddingFactory.create(user_context=planner)

                # Budget: OneToOne with Wedding — create one, then attach categories.
                budget = BudgetFactory.create(wedding=wedding, company=planner.company)
                categories = BudgetCategoryFactory.create_batch(
                    3, budget=budget, wedding=wedding
                )

                # Contracts, Expenses, and Installments
                for _ in range(3):
                    supplier = secrets.choice(suppliers)

                    # NOTE: Contract.clean() raises ValidationError if
                    # status == SIGNED and pdf_file is missing. Since we cannot
                    # upload actual files during seeding, all contracts are
                    # created as DRAFT to avoid this validation.
                    contract = ContractFactory.create(
                        wedding=wedding,
                        supplier=supplier,
                        company=planner.company,
                        status=Contract.StatusChoices.DRAFT,
                    )
                    ItemFactory.create_batch(2, contract=contract, wedding=wedding)

                    # Create Expense linked to Contract.
                    category = secrets.choice(categories)
                    amount = Decimal("3000.00")
                    # Exact division ensures sum of installments
                    # equals actual_amount (BR-F01 integrity check).
                    installment_amount = amount / Decimal("3")

                    expense = ExpenseFactory.create(
                        wedding=wedding,
                        company=planner.company,
                        category=category,
                        contract=contract,
                        name=f"Despesa: {contract.name}",
                        actual_amount=installment_amount * 3,
                        estimated_amount=amount,
                    )

                    # Create 3 installments with mixed statuses.
                    # Their sum must equal expense.actual_amount (BR-F01).

                    # Installment 1: PAID
                    InstallmentFactory.create(
                        expense=expense,
                        company=planner.company,
                        wedding=wedding,
                        installment_number=1,
                        amount=installment_amount,
                        due_date=date.today() - timedelta(days=30),
                        paid_date=date.today() - timedelta(days=28),
                        status=Installment.StatusChoices.PAID,
                    )

                    # Installment 2: OVERDUE (past due, not paid)
                    InstallmentFactory.create(
                        expense=expense,
                        company=planner.company,
                        wedding=wedding,
                        installment_number=2,
                        amount=installment_amount,
                        due_date=date.today() - timedelta(days=5),
                        paid_date=None,
                        status=Installment.StatusChoices.OVERDUE,
                    )

                    # Installment 3: PENDING (future)
                    InstallmentFactory.create(
                        expense=expense,
                        company=planner.company,
                        wedding=wedding,
                        installment_number=3,
                        amount=installment_amount,
                        due_date=date.today() + timedelta(days=45),
                        paid_date=None,
                        status=Installment.StatusChoices.PENDING,
                    )

                # 4. Tasks (Checklist)
                TaskFactory.create_batch(3, wedding=wedding, is_completed=True)
                TaskFactory.create_batch(2, wedding=wedding, is_completed=False)

                # 5. Calendar Events
                EventFactory.create_batch(4, wedding=wedding)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucesso! Criados {num_planners} planners e "
                f"{num_planners * num_weddings} casamentos no total."
            )
        )
