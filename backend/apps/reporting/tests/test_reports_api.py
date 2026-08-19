"""
Testes de integração para as rotas do reports_router (/api/v1/reports/).
"""

from typing import Any, cast
from unittest.mock import patch
from uuid import uuid4

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
class TestReportsAPI:
    """Testes de integração para exportação de relatórios síncronos e assíncronos."""

    def test_export_wedding_report_pdf_success(
        self, auth_client: Any, user: Any
    ) -> None:
        """Gera e baixa relatório PDF com status 200 e headers corretos."""
        wedding = WeddingFactory(company=user.company)
        url = f"/api/v1/reports/weddings/{wedding.uuid}/?format=pdf"
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert (
            response["Content-Disposition"]
            == f'attachment; filename="relatorio-casamento-{wedding.uuid}.pdf"'
        )
        assert response.content.startswith(b"%PDF-")

    def test_export_wedding_report_excel_success(
        self, auth_client: Any, user: Any
    ) -> None:
        """Gera e baixa relatório Excel com status 200 e headers corretos."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.get(
            f"/api/v1/reports/weddings/{wedding.uuid}/?format=excel"
        )
        assert response.status_code == 200
        assert (
            response["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert (
            response["Content-Disposition"]
            == f'attachment; filename="relatorio-casamento-{wedding.uuid}.xlsx"'
        )
        assert response.content.startswith(b"PK\x03\x04")

    def test_export_wedding_report_cross_tenant_returns_404(
        self, auth_client: Any
    ) -> None:
        """Bloqueia exportação de casamento pertencente a outro tenant com HTTP 404."""
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        response = auth_client.get(
            f"/api/v1/reports/weddings/{other_wedding.uuid}/?format=pdf"
        )
        assert response.status_code == 404

    def test_export_wedding_report_unauthenticated_returns_401(
        self, client: Any
    ) -> None:
        """Bloqueia requisição não autenticada com HTTP 401."""
        response = client.get(f"/api/v1/reports/weddings/{uuid4()}/?format=pdf")
        assert response.status_code == 401

    def test_export_wedding_report_async_success(
        self, auth_client: Any, user: Any
    ) -> None:
        """Enfileira geração assíncrona com status 202 e resposta padronizada."""
        from django.tasks import Task

        wedding = WeddingFactory(company=user.company)

        with patch.object(Task, "enqueue") as mock_enqueue:
            response = auth_client.post(
                f"/api/v1/reports/weddings/{wedding.uuid}/async/?format=pdf"
            )
            assert response.status_code == 202
            data = response.json()
            assert data["status"] == "enqueued"
            assert "Geração do relatório" in data["detail"]

            mock_enqueue.assert_called_once_with(
                company_id=str(user.company.uuid),
                user_id=str(user.uuid),
                wedding_id=str(wedding.uuid),
                report_format="pdf",
            )

    def test_export_wedding_report_async_cross_tenant_returns_404(
        self, auth_client: Any
    ) -> None:
        """Bloqueia enfileiramento assíncrono para casamento de outro tenant."""
        other_company = CompanyFactory()
        other_wedding = WeddingFactory(company=other_company)

        response = auth_client.post(
            f"/api/v1/reports/weddings/{other_wedding.uuid}/async/?format=pdf"
        )
        assert response.status_code == 404
