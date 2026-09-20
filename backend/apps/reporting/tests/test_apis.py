"""
Testes de integração para as rotas da API do módulo Reporting.
"""

from typing import Any, cast

import pytest

from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestReportingDashboardAPI:
    """Testes para os endpoints do router de dashboard em Reporting."""

    def test_dashboard_summary_api_success(self, auth_client: Any, user: Any) -> None:
        WeddingFactory(company=user.company)

        response = auth_client.get("/api/v1/dashboard/summary/")
        assert response.status_code == 200
        data = response.json()
        assert "overdue_installments_count" in data
        assert "pending_installments_7d" in data
        assert "urgent_tasks_count" in data
        assert "pending_contracts_count" in data
        assert "critical_weddings" in data
        assert "upcoming_installments" in data
        assert "overdue_installments" in data
        assert "urgent_tasks" in data
        assert "pending_contracts" in data

    def test_dashboard_wedding_api_success(self, auth_client: Any, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)

        response = auth_client.get(f"/api/v1/dashboard/wedding/{wedding.uuid}/")
        assert response.status_code == 200
        data = response.json()
        assert "days_until_wedding" in data
        assert "budget_percentage_used" in data
        assert "tasks_completed" in data
        assert "tasks_total" in data
        assert "contracts_signed" in data
        assert "contracts_total" in data
        assert "total_allocated" in data
        assert "total_spent" in data

    def test_dashboard_wedding_api_unauthorized_cross_tenant(
        self, auth_client: Any
    ) -> None:
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        response = auth_client.get(f"/api/v1/dashboard/wedding/{other_wedding.uuid}/")
        assert response.status_code == 404

    def test_dashboard_chart_cash_flow_api_success(
        self, auth_client: Any, user: Any
    ) -> None:
        response = auth_client.get("/api/v1/dashboard/chart/cash-flow/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 12
        assert data[0]["month"] == 1
        assert "paid" in data[0]
        assert "pending" in data[0]

        # Com query param de ano
        response_year = auth_client.get("/api/v1/dashboard/chart/cash-flow/?year=2026")
        assert response_year.status_code == 200
        data_year = response_year.json()
        assert len(data_year) == 12

    def test_dashboard_chart_task_progress_api_success(
        self, auth_client: Any, user: Any
    ) -> None:
        wedding = WeddingFactory(company=user.company)
        from apps.scheduler.tests.factories import TaskFactory

        TaskFactory(wedding=wedding, company=user.company, is_completed=True)

        response = auth_client.get("/api/v1/dashboard/chart/task-progress/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["wedding_uuid"] == str(wedding.uuid)
        assert "progress_pct" in data[0]
        assert "total_tasks" in data[0]
        assert "completed_tasks" in data[0]

    def test_dashboard_operations_api_success(
        self, auth_client: Any, user: Any
    ) -> None:
        WeddingFactory(company=user.company)

        response = auth_client.get("/api/v1/dashboard/operations/")
        assert response.status_code == 200
        data = response.json()
        assert "upcoming_weddings" in data
        assert "urgent_tasks" in data
        assert "pending_contracts" in data
        assert isinstance(data["upcoming_weddings"], list)
        assert isinstance(data["urgent_tasks"], list)
        assert isinstance(data["pending_contracts"], list)

    def test_dashboard_endpoints_unauthenticated(self, client: Any) -> None:
        res_cash = client.get("/api/v1/dashboard/chart/cash-flow/")
        assert res_cash.status_code == 401

        res_task = client.get("/api/v1/dashboard/chart/task-progress/")
        assert res_task.status_code == 401

        res_ops = client.get("/api/v1/dashboard/operations/")
        assert res_ops.status_code == 401
