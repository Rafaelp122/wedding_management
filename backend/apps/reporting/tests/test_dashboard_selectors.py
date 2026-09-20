"""
Testes unitários e de integração para Dashboard Selectors do módulo Reporting.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast
from unittest.mock import patch

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.reporting.selectors import (
    cash_flow_by_month,
    dashboard_operations_selector,
    dashboard_summary_selector,
    overdue_installments_detail,
    pending_contracts_detail,
    tasks_progress_by_wedding,
    upcoming_installments_detail,
    urgent_tasks_detail,
    wedding_overview_selector,
)
from apps.scheduler.tests.factories import TaskFactory
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestDashboardSelectors:
    """Testes para selectors do painel de dashboard no app Reporting."""

    def test_dashboard_summary_selector_success(self, user: Any) -> None:
        today = date.today()
        wedding = WeddingFactory(
            company=user.company,
            date=today + timedelta(days=20),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        category = BudgetCategoryFactory(wedding=wedding)
        expense1 = ExpenseFactory(wedding=wedding, category=category, contract=None)

        # 1. Parcela atrasada (1000.00)
        InstallmentFactory(
            expense=expense1,
            amount=1000.00,
            due_date=today - timedelta(days=5),
            status="PENDING",
        )

        # 2. Parcela a vencer em 7 dias (2500.00)
        InstallmentFactory(
            expense=expense1,
            amount=2500.00,
            due_date=today + timedelta(days=3),
            status="PENDING",
        )

        # 3. Tarefa urgente
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=1),
        )

        # 4. Contrato pendente
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="PENDING",
            total_amount=5000.00,
        )

        summary = dashboard_summary_selector(company=user.company)

        assert summary["overdue_installments_count"] == 1
        assert summary["overdue_installments_amount"] == "1000.00"
        assert summary["pending_installments_7d"] == "2500.00"
        assert summary["urgent_tasks_count"] == 1
        assert summary["pending_contracts_count"] == 1
        assert len(summary["critical_weddings"]) == 1
        assert summary["critical_weddings"][0]["uuid"] == wedding.uuid
        assert summary["critical_weddings"][0]["days_until"] == 20
        assert len(summary["upcoming_installments"]) == 1
        assert summary["upcoming_installments"][0]["amount"] == "2500.00"
        assert len(summary["overdue_installments"]) == 1
        assert summary["overdue_installments"][0]["amount"] == "1000.00"
        assert len(summary["urgent_tasks"]) == 1
        assert len(summary["pending_contracts"]) == 1
        assert summary["pending_contracts"][0]["supplier_name"] == supplier.name

    def test_dashboard_summary_selector_empty_company(self, user: Any) -> None:
        summary = dashboard_summary_selector(company=user.company)

        assert summary["pending_installments_7d"] == "0.00"
        assert summary["urgent_tasks_count"] == 0
        assert summary["overdue_installments_amount"] == "0.00"
        assert summary["overdue_installments_count"] == 0
        assert summary["pending_contracts_count"] == 0
        assert summary["critical_weddings"] == []
        assert summary["upcoming_installments"] == []
        assert summary["overdue_installments"] == []
        assert summary["urgent_tasks"] == []
        assert summary["pending_contracts"] == []

    def test_dashboard_summary_selector_multitenancy(self, user: Any) -> None:
        other_company = CompanyFactory()
        today = date.today()
        wedding = WeddingFactory(
            company=other_company,
            date=today + timedelta(days=10),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        TaskFactory(
            wedding=wedding,
            company=other_company,
            is_completed=False,
            due_date=today - timedelta(days=1),
        )

        summary = dashboard_summary_selector(company=user.company)
        assert summary["urgent_tasks_count"] == 0
        assert summary["critical_weddings"] == []

    def test_dashboard_summary_selector_logs(self, user: Any) -> None:
        with patch(
            "apps.reporting.selectors.dashboard_selectors.logger"
        ) as mock_logger:
            dashboard_summary_selector(company=user.company)

        mock_logger.info.assert_any_call(
            f"Computando resumo do dashboard para company_id={user.company.id}"
        )
        assert any(
            "Dashboard resumo computado" in call[0][0]
            for call in mock_logger.info.call_args_list
        )

    def test_wedding_overview_selector_success(self, user: Any) -> None:
        today = date.today()
        wedding = WeddingFactory(company=user.company, date=today + timedelta(days=60))
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=10000.00
        )
        category = BudgetCategoryFactory(budget=budget, allocated_budget=5000.00)
        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            company=user.company,
            actual_amount=2000.00,
            contract=None,
        )

        # Tarefas
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=today - timedelta(days=1),
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=2),
            title="Tarefa Urgente",
        )

        # Contratos
        supplier = SupplierFactory(company=user.company)
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            total_amount=5000.00,
            pdf_file="contracts/dummy.pdf",
            signed_date=today,
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="PENDING",
            total_amount=3000.00,
        )

        # Parcelas
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today - timedelta(days=10),
            status=Installment.StatusChoices.PAID,
            paid_date=today - timedelta(days=10),
            wedding=wedding,
            company=user.company,
        )
        InstallmentFactory(
            expense=expense,
            amount=1000.00,
            due_date=today + timedelta(days=30),
            status=Installment.StatusChoices.PENDING,
            wedding=wedding,
            company=user.company,
        )

        overview = wedding_overview_selector(
            company=user.company, wedding_uuid=wedding.uuid
        )

        assert overview["days_until_wedding"] == 60
        assert overview["budget_percentage_used"] == 10.0
        assert overview["tasks_completed"] == 1
        assert overview["tasks_total"] == 2
        assert overview["contracts_signed"] == 1
        assert overview["contracts_total"] == 2
        assert len(overview["upcoming_installments"]) == 1
        assert len(overview["urgent_tasks"]) == 1
        assert overview["urgent_tasks"][0]["title"] == "Tarefa Urgente"
        assert len(overview["categories_summary"]) == 1
        assert overview["categories_summary"][0]["name"] == category.name
        assert overview["categories_summary"][0]["percentage"] == 20
        assert overview["total_allocated"] == "5000.00"
        assert overview["total_spent"] == "1000.00"

    def test_wedding_overview_selector_not_found(self, user: Any) -> None:
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        with pytest.raises(ObjectNotFoundError):
            wedding_overview_selector(
                company=user.company, wedding_uuid=other_wedding.uuid
            )

    def test_wedding_overview_selector_logs(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        with patch(
            "apps.reporting.selectors.dashboard_selectors.logger"
        ) as mock_logger:
            wedding_overview_selector(company=user.company, wedding_uuid=wedding.uuid)

        assert any(
            f"uuid={wedding.uuid}" in call[0][0]
            for call in mock_logger.info.call_args_list
        )
        assert any(
            "Visão geral do casamento" in call[0][0]
            for call in mock_logger.info.call_args_list
        )

    def test_contract_summary_selector_annotate_financial_totals(
        self, user: Any
    ) -> None:
        """Valida anotação de expense_id e total_paid via ContractSummarySelector."""
        from decimal import Decimal

        from apps.logistics.models import Contract
        from apps.reporting.selectors.summaries import ContractSummarySelector

        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        contract = cast(
            Contract,
            ContractFactory(
                wedding=wedding,
                company=user.company,
                supplier=supplier,
                total_amount=Decimal("1000.00"),
            ),
        )
        category = BudgetCategoryFactory(wedding=wedding)
        expense = cast(
            Any,
            ExpenseFactory(
                wedding=wedding,
                category=category,
                contract=contract,
                actual_amount=contract.total_amount,
                company=user.company,
            ),
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("400.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
            company=user.company,
        )

        qs = Contract.objects.for_tenant(user.company).filter(pk=contract.pk)
        annotated_qs = ContractSummarySelector.annotate_financial_totals(qs)
        item = cast(Any, annotated_qs.first())

        assert item is not None
        assert item.expense_id == expense.uuid
        assert item.total_paid == Decimal("400.00")

    def test_cash_flow_by_month_success(self, user: Any) -> None:
        """
        Valida que cash_flow_by_month retorna exatamente 12 meses preenchidos
        e agrega valores corretamente.
        """
        wedding = WeddingFactory(company=user.company)
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)

        # Janeiro (mês 1): parcela PAGA 1200.00
        InstallmentFactory(
            expense=expense,
            amount=1200.00,
            due_date=date(2026, 1, 15),
            status=Installment.StatusChoices.PAID,
            paid_date=date(2026, 1, 15),
            wedding=wedding,
            company=user.company,
        )
        # Janeiro (mês 1): parcela PENDENTE 800.00
        InstallmentFactory(
            expense=expense,
            amount=800.00,
            due_date=date(2026, 1, 20),
            status=Installment.StatusChoices.PENDING,
            wedding=wedding,
            company=user.company,
        )
        # Fevereiro (mês 2): parcela ATRASADA (OVERDUE) 500.00
        InstallmentFactory(
            expense=expense,
            amount=500.00,
            due_date=date(2026, 2, 10),
            status=Installment.StatusChoices.OVERDUE,
            wedding=wedding,
            company=user.company,
        )
        # Outro ano (2025): não deve aparecer no cômputo de 2026
        InstallmentFactory(
            expense=expense,
            amount=9999.00,
            due_date=date(2025, 1, 15),
            status=Installment.StatusChoices.PAID,
            paid_date=date(2025, 1, 15),
            wedding=wedding,
            company=user.company,
        )

        flow = cash_flow_by_month(company=user.company, year=2026)

        assert len(flow) == 12
        assert flow[0] == {"month": 1, "paid": "1200.00", "pending": "800.00"}
        assert flow[1] == {"month": 2, "paid": "0.00", "pending": "500.00"}
        for i in range(2, 12):
            assert flow[i] == {"month": i + 1, "paid": "0.00", "pending": "0.00"}

    def test_cash_flow_by_month_multitenancy(self, user: Any) -> None:
        """Valida isolamento multi-tenant de cash_flow_by_month."""
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)
        other_category = BudgetCategoryFactory(wedding=other_wedding)
        other_expense = ExpenseFactory(
            wedding=other_wedding, category=other_category, contract=None
        )

        InstallmentFactory(
            expense=other_expense,
            amount=5000.00,
            due_date=date(2026, 3, 10),
            status=Installment.StatusChoices.PAID,
            paid_date=date(2026, 3, 10),
            wedding=other_wedding,
            company=other_company,
        )

        flow = cash_flow_by_month(company=user.company, year=2026)
        assert len(flow) == 12
        assert flow[2] == {"month": 3, "paid": "0.00", "pending": "0.00"}

    def test_upcoming_and_overdue_installments_detail(self, user: Any) -> None:
        """
        Valida que upcoming_installments_detail e overdue_installments_detail
        retornam dados formatados.
        """
        today = date(2026, 6, 15)
        wedding = WeddingFactory(
            company=user.company,
            bride_name="Juliana",
            groom_name="Rodrigo",
        )
        category = BudgetCategoryFactory(wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=category, contract=None)

        # Parcela a vencer em 3 dias
        inst_upcoming = cast(
            Any,
            InstallmentFactory(
                expense=expense,
                amount=1500.00,
                due_date=today + timedelta(days=3),
                status=Installment.StatusChoices.PENDING,
                installment_number=1,
                wedding=wedding,
                company=user.company,
            ),
        )

        # Parcela vencida há 5 dias
        inst_overdue = cast(
            Any,
            InstallmentFactory(
                expense=expense,
                amount=2000.00,
                due_date=today - timedelta(days=5),
                status=Installment.StatusChoices.OVERDUE,
                installment_number=2,
                wedding=wedding,
                company=user.company,
            ),
        )

        # Outra empresa (multi-tenant)
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)
        other_cat = BudgetCategoryFactory(wedding=other_wedding)
        other_exp = ExpenseFactory(
            wedding=other_wedding, category=other_cat, contract=None
        )
        InstallmentFactory(
            expense=other_exp,
            amount=9999.00,
            due_date=today + timedelta(days=2),
            status=Installment.StatusChoices.PENDING,
            wedding=other_wedding,
            company=other_company,
        )

        upcoming = upcoming_installments_detail(
            company=user.company, today=today, limit=10
        )
        assert len(upcoming) == 1
        assert upcoming[0]["uuid"] == inst_upcoming.uuid
        assert upcoming[0]["wedding_name"] == "Juliana e Rodrigo"
        assert upcoming[0]["amount"] == "1500.00"
        assert upcoming[0]["installment_number"] == 1
        assert upcoming[0]["status"] == "PENDING"

        overdue = overdue_installments_detail(
            company=user.company, today=today, limit=10
        )
        assert len(overdue) == 1
        assert overdue[0]["uuid"] == inst_overdue.uuid
        assert overdue[0]["wedding_name"] == "Juliana e Rodrigo"
        assert overdue[0]["amount"] == "2000.00"
        assert overdue[0]["installment_number"] == 2
        assert overdue[0]["status"] == "OVERDUE"

    def test_tasks_progress_by_wedding(self, user: Any) -> None:
        """
        Valida que tasks_progress_by_wedding agrupa tarefas por casamento
        e calcula percentual.
        """
        today = date.today()
        wedding1 = WeddingFactory(
            company=user.company,
            bride_name="Marina",
            groom_name="Lucas",
            date=today + timedelta(days=60),
        )
        wedding2 = WeddingFactory(
            company=user.company,
            bride_name="Camila",
            groom_name="Felipe",
            date=today + timedelta(days=90),
        )

        # Casamento 1: 4 tarefas (3 concluídas -> 75%)
        for _ in range(3):
            TaskFactory(wedding=wedding1, company=user.company, is_completed=True)
        TaskFactory(wedding=wedding1, company=user.company, is_completed=False)

        # Casamento 2: 2 tarefas (1 concluída -> 50%)
        TaskFactory(wedding=wedding2, company=user.company, is_completed=True)
        TaskFactory(wedding=wedding2, company=user.company, is_completed=False)

        # Outra empresa
        other_company = CompanyFactory()
        other_w = WeddingFactory(company=other_company)
        TaskFactory(wedding=other_w, company=other_company, is_completed=True)

        progress = tasks_progress_by_wedding(company=user.company)
        assert len(progress) == 2
        # Ordenado por volume total decrescente: wedding1 (4 tarefas) primeiro
        assert progress[0]["wedding_uuid"] == wedding1.uuid
        assert progress[0]["wedding_name"] == "Marina e Lucas"
        assert progress[0]["total_tasks"] == 4
        assert progress[0]["completed_tasks"] == 3
        assert progress[0]["progress_pct"] == 75

        assert progress[1]["wedding_uuid"] == wedding2.uuid
        assert progress[1]["wedding_name"] == "Camila e Felipe"
        assert progress[1]["total_tasks"] == 2
        assert progress[1]["completed_tasks"] == 1
        assert progress[1]["progress_pct"] == 50

    def test_tasks_progress_by_wedding_filter_year(self, user: Any) -> None:
        """Valida filtro de ano em tasks_progress_by_wedding."""
        wedding_2027 = WeddingFactory(
            company=user.company,
            date=date(2027, 5, 1),
            bride_name="Ana",
            groom_name="Bruno",
        )
        wedding_2028 = WeddingFactory(
            company=user.company,
            date=date(2028, 5, 1),
            bride_name="Clara",
            groom_name="Diego",
        )
        TaskFactory(wedding=wedding_2027, company=user.company, is_completed=True)
        TaskFactory(wedding=wedding_2028, company=user.company, is_completed=True)

        progress_2027 = tasks_progress_by_wedding(company=user.company, year=2027)
        assert len(progress_2027) == 1
        assert progress_2027[0]["wedding_uuid"] == wedding_2027.uuid

    def test_urgent_tasks_detail(self, user: Any) -> None:
        """Valida busca de tarefas atrasadas no tenant."""
        today = date(2026, 4, 10)
        wedding = WeddingFactory(
            company=user.company,
            bride_name="Sofia",
            groom_name="Gabriel",
        )
        task_urgent = cast(
            Any,
            TaskFactory(
                wedding=wedding,
                company=user.company,
                title="Degustação do Bolo",
                due_date=today - timedelta(days=2),
                is_completed=False,
            ),
        )
        # Tarefa já concluída: não deve vir
        TaskFactory(
            wedding=wedding,
            company=user.company,
            title="Contratar Banda",
            due_date=today - timedelta(days=3),
            is_completed=True,
        )

        tasks = urgent_tasks_detail(company=user.company, today=today, limit=10)
        assert len(tasks) == 1
        assert tasks[0]["uuid"] == task_urgent.uuid
        assert tasks[0]["wedding_name"] == "Sofia e Gabriel"
        assert tasks[0]["title"] == "Degustação do Bolo"
        assert tasks[0]["due_date"] == task_urgent.due_date

    def test_pending_contracts_detail(self, user: Any) -> None:
        """
        Valida busca de contratos pendentes com detalhes de fornecedor e casamento.
        """
        wedding = WeddingFactory(
            company=user.company,
            bride_name="Paula",
            groom_name="Marcos",
        )
        supplier = SupplierFactory(company=user.company, name="Buffet Delícias")
        contract = cast(
            Any,
            ContractFactory(
                wedding=wedding,
                company=user.company,
                supplier=supplier,
                status="PENDING",
                total_amount=Decimal("15000.00"),
            ),
        )
        # Contrato assinado: não deve vir
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="SIGNED",
            total_amount=Decimal("5000.00"),
            pdf_file="contracts/dummy.pdf",
            signed_date=date.today(),
        )

        contracts = pending_contracts_detail(company=user.company, limit=10)
        assert len(contracts) == 1
        assert contracts[0]["uuid"] == contract.uuid
        assert contracts[0]["wedding_name"] == "Paula e Marcos"
        assert contracts[0]["supplier_name"] == "Buffet Delícias"
        assert contracts[0]["total_amount"] == "15000.00"
        assert contracts[0]["status"] == "PENDING"

    def test_dashboard_operations_selector(self, user: Any) -> None:
        """
        Valida consolidação de operações
        (próximos casamentos, tarefas e contratos Top 5).
        """
        today = date.today()
        wedding = WeddingFactory(
            company=user.company,
            bride_name="Fernanda",
            groom_name="Thiago",
            date=today + timedelta(days=15),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        supplier = SupplierFactory(company=user.company, name="DJ Som & Luz")
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            status="DRAFT",
            total_amount=Decimal("3500.00"),
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            title="Aprovar playlist",
            due_date=today - timedelta(days=1),
            is_completed=False,
        )

        operations = dashboard_operations_selector(company=user.company)
        assert "upcoming_weddings" in operations
        assert "urgent_tasks" in operations
        assert "pending_contracts" in operations

        assert len(operations["upcoming_weddings"]) >= 1
        assert operations["upcoming_weddings"][0]["uuid"] == wedding.uuid
        assert operations["upcoming_weddings"][0]["days_until"] == 15

        assert len(operations["urgent_tasks"]) == 1
        assert operations["urgent_tasks"][0]["title"] == "Aprovar playlist"

        assert len(operations["pending_contracts"]) == 1
        assert operations["pending_contracts"][0]["supplier_name"] == "DJ Som & Luz"
