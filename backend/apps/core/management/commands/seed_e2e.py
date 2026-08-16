"""Comando de seed leve e determinístico para testes E2E.

Cria superusuário, planner, casamentos e entidades com dados fixos
e previsíveis necessários para a suíte Playwright E2E.

Nota de Idempotência:
    A execução deste comando limpa previamente as entidades do planner E2E
    para garantir que os testes rodem em um ambiente previsível.

Uso:
    python manage.py seed_e2e
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.finances.models import Budget, Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.models import Contract, Supplier
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.models import Event, Task
from apps.scheduler.tests.factories import EventFactory, TaskFactory
from apps.users.tests.factories import AdminFactory, UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


class Command(BaseCommand):
    """Comando de gerenciamento para criação de seed determinístico E2E."""

    help = "Popula o banco com dados mínimos e determinísticos para a suíte E2E"

    @transaction.atomic
    def handle(self, *args: Any, **kwargs: Any) -> None:
        """Executa a rotina de criação determinística de dados para E2E.

        Args:
            *args: Argumentos posicionais do comando.
            **kwargs: Argumentos chave-valor passados via CLI.
        """
        self.stdout.write(
            self.style.MIGRATE_LABEL("Iniciando seed determinístico E2E...")
        )

        User = get_user_model()

        # 1. Superusuário Admin
        admin = User.objects.filter(email="admin@admin.com").first()
        if not admin:
            admin = AdminFactory.create(
                email="admin@admin.com",
                first_name="Admin",
                last_name="Master",
            )
            self.stdout.write(self.style.SUCCESS("  ✓ Admin: admin@admin.com"))

        # 2. Planner E2E
        planner = User.objects.filter(email="planner@example.com").first()
        if not planner:
            planner = UserFactory.create(
                email="planner@example.com",
                password="password123",  # pragma: allowlist secret # noqa: S106
                first_name="Planner",
                last_name="E2E",
            )
            self.stdout.write(
                self.style.SUCCESS("  ✓ Planner E2E: planner@example.com")
            )

        # 3. Staff E2E
        staff = User.objects.filter(email="staff@example.com").first()
        if not staff:
            staff = UserFactory.create(
                email="staff@example.com",
                password="password123",  # pragma: allowlist secret # noqa: S106
                first_name="Staff",
                last_name="E2E",
                is_staff=True,
                is_superuser=False,
            )
            self.stdout.write(self.style.SUCCESS("  ✓ Staff E2E: staff@example.com"))

        company = planner.company

        # Limpar dados anteriores do planner para garantir idempotência E2E
        Task.objects.filter(wedding__company=company).delete()
        Event.objects.filter(wedding__company=company).delete()
        Expense.objects.filter(company=company).delete()
        Contract.objects.filter(company=company).delete()
        Budget.objects.filter(company=company).delete()
        Supplier.objects.filter(company=company).delete()
        Wedding.objects.filter(company=company).delete()

        # 4. Casamento Concluído
        # Nota: skip_clean=True é necessário para casamentos concluídos com data no
        # passado, pois BaseModel.full_clean() exige datas futuras durante a
        # validação de criação (ADR-011).
        completed_wedding = WeddingFactory.build(
            user_context=planner,
            groom_name="Carlos",
            bride_name="Ana",
            status=Wedding.StatusChoices.COMPLETED,
            date=timezone.now().date() - timedelta(days=30),
        )
        completed_wedding.save(skip_clean=True)

        # 5. Casamento Em Andamento (usado nos testes de Dashboard e CRUD)
        active_wedding = WeddingFactory.create(
            user_context=planner,
            groom_name="João",
            bride_name="Maria",
            status=Wedding.StatusChoices.IN_PROGRESS,
            date=timezone.now().date() + timedelta(days=30),
        )

        # 6. Fornecedor determinístico
        supplier = SupplierFactory.create(
            company=company,
            name="Fornecedor Festas E2E",
            phone="(11) 99999-0000",
        )

        # 7. Orçamento e Categorias
        budget = BudgetFactory.create(
            wedding=active_wedding,
            company=company,
            total_estimated=Decimal("50000.00"),
        )
        BudgetCategoryFactory.create(
            budget=budget, wedding=active_wedding, name="Decoração"
        )
        cat_buf = BudgetCategoryFactory.create(
            budget=budget, wedding=active_wedding, name="Buffet"
        )
        BudgetCategoryFactory.create(
            budget=budget, wedding=active_wedding, name="Música"
        )

        # 8. Contrato assinado com despesas e parcelas
        contract = ContractFactory.create(
            wedding=active_wedding,
            supplier=supplier,
            company=company,
            name="Contrato Buffet",
            status=Contract.StatusChoices.SIGNED,
            signed_date=date.today() - timedelta(days=10),
            total_amount=Decimal("15000.00"),
            pdf_file=ContentFile(b"dummy pdf content", name="contract.pdf"),
        )
        ItemFactory.create_batch(2, contract=contract, wedding=active_wedding)

        expense = ExpenseFactory.create(
            wedding=active_wedding,
            company=company,
            category=cat_buf,
            contract=contract,
            name=f"Despesa: {contract.name}",
            actual_amount=Decimal("15000.00"),
            estimated_amount=Decimal("15000.00"),
        )

        # Parcelas determinísticas instanciadas explicitamente para garantir
        # datas relativas exatas exigidas pelas asserções dos KPIs do Dashboard:
        # 1. Parcela Pago (Vencida a 30 dias, Paga a 28 dias)
        InstallmentFactory.create(
            expense=expense,
            company=company,
            wedding=active_wedding,
            installment_number=1,
            amount=Decimal("5000.00"),
            due_date=date.today() - timedelta(days=30),
            paid_date=date.today() - timedelta(days=28),
            status=Installment.StatusChoices.PAID,
        )

        # 2. Parcela Vencida (Vencida a 5 dias) -> Para KPI "Parcelas Vencidas"
        InstallmentFactory.create(
            expense=expense,
            company=company,
            wedding=active_wedding,
            installment_number=2,
            amount=Decimal("5000.00"),
            due_date=date.today() - timedelta(days=5),
            paid_date=None,
            status=Installment.StatusChoices.OVERDUE,
        )

        # 3. Parcela a Vencer (Vence em 5 dias) -> Para KPI "Parcelas a Vencer"
        InstallmentFactory.create(
            expense=expense,
            company=company,
            wedding=active_wedding,
            installment_number=3,
            amount=Decimal("5000.00"),
            due_date=date.today() + timedelta(days=5),
            paid_date=None,
            status=Installment.StatusChoices.PENDING,
        )

        # 9. Tarefas determinísticas para KPI "Tarefas Atrasadas"
        TaskFactory.create(
            wedding=active_wedding,
            title="Tarefa Atrasada E2E",
            is_completed=False,
            due_date=date.today() - timedelta(days=2),
        )
        TaskFactory.create(
            wedding=active_wedding,
            title="Tarefa Pendente E2E",
            is_completed=False,
            due_date=date.today() + timedelta(days=10),
        )
        TaskFactory.create_batch(3, wedding=active_wedding, is_completed=True)

        # 10. Eventos
        EventFactory.create_batch(4, wedding=active_wedding)

        self.stdout.write(
            self.style.SUCCESS("✓ Seed determinístico E2E concluído com sucesso!")
        )
