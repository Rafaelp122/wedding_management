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

    def test_dashboard_wedding_api_unauthorized_cross_tenant(
        self, auth_client: Any
    ) -> None:
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        response = auth_client.get(f"/api/v1/dashboard/wedding/{other_wedding.uuid}/")
        assert response.status_code == 404
