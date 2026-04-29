import logging

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.events.tests.factories import EventFactory
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.tests.appointment_factories import AppointmentFactory
from apps.users.models import User


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Gera dados iniciais para desenvolvimento (Faker/FactoryBoy)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Iniciando seed de dados...")

        # 1. Cria usuário e a Company (via signal)
        user, created = User.objects.get_or_create(
            email="organizador@exemplo.com",
            defaults={
                "first_name": "Rafael",
                "last_name": "Organizador",
                "is_active": True,
            },
        )
        if created:
            user.set_password("admin123")
            user.save()

        company = user.company
        self.stdout.write(f"Usuário e Empresa '{company}' prontos.")

        # 2. Cria Eventos (Casamentos)
        event = EventFactory(company=company)
        self.stdout.write(f"Evento '{event.name}' criado.")

        # 3. Cria Infraestrutura Financeira e Logística
        # Budget e Categories são criados via Service, mas aqui usamos Factories para volume
        category = BudgetCategoryFactory(event=event)
        supplier = SupplierFactory(company=company)
        contract = ContractFactory(
            event=event, supplier=supplier, budget_category=category
        )

        # 4. Cria Operacional
        ExpenseFactory(event=event, category=category, contract=contract)
        InstallmentFactory(event=event)
        ItemFactory(event=event, contract=contract)

        # 5. Cria Agenda
        AppointmentFactory(company=company, event=event)

        self.stdout.write(self.style.SUCCESS("Seed finalizado com sucesso!"))
