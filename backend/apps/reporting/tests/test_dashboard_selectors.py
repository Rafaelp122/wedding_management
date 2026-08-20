"""
Testes unitários e de integração para Dashboard Selectors do módulo Reporting.
"""

from datetime import date, timedelta
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
    dashboard_summary_selector,
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

    def test_dashboard_summary_selector_empty_company(self, user: Any) -> None:
        summary = dashboard_summary_selector(company=user.company)

        assert summary["pending_installments_7d"] == "0.00"
        assert summary["urgent_tasks_count"] == 0
        assert summary["overdue_installments_amount"] == "0.00"
        assert summary["overdue_installments_count"] == 0
        assert summary["pending_contracts_count"] == 0
        assert summary["critical_weddings"] == []

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
