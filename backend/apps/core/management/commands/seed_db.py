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
from decimal import ROUND_DOWN, Decimal

from django.core.files.base import ContentFile
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
from apps.weddings.models import Wedding
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

        from django.contrib.auth import get_user_model

        User = get_user_model()
        e2e_planner = User.objects.filter(email="planner@example.com").first()
        if not e2e_planner:
            e2e_planner = UserFactory.create(
                email="planner@example.com",
                password="password123",  # pragma: allowlist secret # noqa: S106
                first_name="Planner",
                last_name="E2E",
            )
            self.stdout.write(
                self.style.SUCCESS("  ✓ Planner E2E: planner@example.com / password123")
            )

        e2e_staff = User.objects.filter(email="staff@example.com").first()
        if not e2e_staff:
            e2e_staff = UserFactory.create(
                email="staff@example.com",
                password="password123",  # pragma: allowlist secret # noqa: S106
                first_name="Staff",
                last_name="E2E",
                is_staff=True,
                is_superuser=False,
            )
            self.stdout.write(
                self.style.SUCCESS("  ✓ Staff E2E: staff@example.com / password123")
            )
        planners = [e2e_planner, *UserFactory.create_batch(num_planners)]
        self.stdout.write(
            self.style.SUCCESS(f"  ✓ {num_planners + 1} planners criados")
        )

        for planner in planners:
            suppliers = SupplierFactory.create_batch(
                5,
                company=planner.company,
                phone="(11) 99999-0000",
            )

            for i in range(num_weddings):
                if i == 0 and num_weddings > 1:
                    wedding = WeddingFactory.create(user_context=planner)
                    wedding.status = Wedding.StatusChoices.COMPLETED
                    wedding.date = timezone.now().date() - timedelta(days=30)
                    wedding.save(skip_clean=True)
                else:
                    wedding = WeddingFactory.create(user_context=planner)

                budget = BudgetFactory.create(wedding=wedding, company=planner.company)
                categories = BudgetCategoryFactory.create_batch(
                    3, budget=budget, wedding=wedding
                )

                for c_idx in range(3):
                    supplier = secrets.choice(suppliers)

                    status = (
                        Contract.StatusChoices.SIGNED
                        if c_idx < 2
                        else Contract.StatusChoices.DRAFT
                    )
                    signed_date = (
                        date.today() - timedelta(days=10)
                        if status == Contract.StatusChoices.SIGNED
                        else None
                    )
                    pdf_file = (
                        ContentFile(b"dummy pdf content", name="contract.pdf")
                        if status == Contract.StatusChoices.SIGNED
                        else None
                    )

                    contract = ContractFactory.create(
                        wedding=wedding,
                        supplier=supplier,
                        company=planner.company,
                        status=status,
                        signed_date=signed_date,
                        pdf_file=pdf_file,
                    )
                    ItemFactory.create_batch(2, contract=contract, wedding=wedding)

                    category = secrets.choice(categories)

                    expense = ExpenseFactory.create(
                        wedding=wedding,
                        company=planner.company,
                        category=category,
                        contract=contract,
                        name=f"Despesa: {contract.name}",
                        actual_amount=contract.total_amount,
                        estimated_amount=contract.total_amount,
                    )

                    installment_amount = (
                        contract.total_amount / Decimal("3")
                    ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                    remainder_amount = contract.total_amount - (
                        installment_amount * Decimal("2")
                    )

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

                    if status == Contract.StatusChoices.SIGNED:
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
                    else:
                        InstallmentFactory.create(
                            expense=expense,
                            company=planner.company,
                            wedding=wedding,
                            installment_number=2,
                            amount=installment_amount,
                            due_date=date.today() + timedelta(days=5),
                            paid_date=None,
                            status=Installment.StatusChoices.PENDING,
                        )

                    InstallmentFactory.create(
                        expense=expense,
                        company=planner.company,
                        wedding=wedding,
                        installment_number=3,
                        amount=remainder_amount,
                        due_date=date.today() + timedelta(days=45),
                        paid_date=None,
                        status=Installment.StatusChoices.PENDING,
                    )

                TaskFactory.create_batch(3, wedding=wedding, is_completed=True)
                TaskFactory.create(wedding=wedding, is_completed=False)
                TaskFactory.create(
                    wedding=wedding,
                    is_completed=False,
                    due_date=date.today() - timedelta(days=2),
                )

                EventFactory.create_batch(4, wedding=wedding)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucesso! Criados {len(planners)} planners e "
                f"{len(planners) * num_weddings} casamentos no total."
            )
        )
