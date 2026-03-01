import secrets

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    InstallmentFactory,
)
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.tests.factories import EventFactory

# Importação das fábricas
from apps.users.tests.factories import AdminFactory, UserFactory
from apps.weddings.tests.factories import WeddingFactory


class Command(BaseCommand):
    help = "Popula o banco com quantidades customizáveis de usuários e casamentos"

    def add_arguments(self, parser):
        # Define o número de Planners (Usuários)
        parser.add_argument(
            "--planners",
            type=int,
            default=2,
            help="Número de Planners (usuários) a serem criados",
        )
        # Define o número de Casamentos por Planner
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
                f"Iniciando seed: {num_planners} planners com {num_weddings} "
                "casamentos cada..."
            )
        )

        # 1. Superusuário
        if (
            not AdminFactory._get_manager(AdminFactory._meta.model)
            .filter(is_superuser=True)
            .exists()
        ):
            AdminFactory.create(email="admin@admin.com", name="Admin Master")

        # 2. Criar Planners baseado no parâmetro
        planners = UserFactory.create_batch(num_planners)

        for planner in planners:
            # Criar um pool de fornecedores para o planner
            suppliers = SupplierFactory.create_batch(5, planner=planner)

            # 3. Criar Casamentos baseado no parâmetro
            weddings = WeddingFactory.create_batch(num_weddings, planner=planner)

            for wedding in weddings:
                # Gerar estrutura financeira e logística básica
                BudgetCategoryFactory.create_batch(3, wedding=wedding)

                for _ in range(3):
                    supplier = secrets.choice(suppliers)

                    contract = ContractFactory.create(
                        wedding=wedding, supplier=supplier
                    )
                    ItemFactory.create_batch(2, contract=contract, wedding=wedding)

                    if hasattr(contract, "expense"):
                        InstallmentFactory.create_batch(3, expense=contract.expense)

                # Agenda
                EventFactory.create_batch(4, wedding=wedding)

        self.stdout.write(
            self.style.SUCCESS(
                f"Sucesso! Criados {num_planners} planners e "
                f"{num_planners * num_weddings} casamentos no total."
            )
        )
