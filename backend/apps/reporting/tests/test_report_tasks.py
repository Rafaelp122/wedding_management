"""
Testes unitários para as background tasks do app reporting (django.tasks).
"""

from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from apps.notifications.models import Notification
from apps.reporting.services import ReportGenerationService
from apps.reporting.tasks import generate_wedding_report_task
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestReportTasks:
    """Valida o ciclo da background task de relatórios e notificações."""

    def test_generate_wedding_report_task_executes_and_creates_notification(
        self,
    ) -> None:
        """Valida que a task gera relatório e cria notificação in-app."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        mock_storage = MagicMock()
        mock_storage.upload_bytes.return_value = "reports/mock-saved.pdf"
        mock_storage.generate_presigned_get_url.return_value = (
            "https://r2.com/signed-report.pdf"
        )
        ReportGenerationService._set_storage_service(mock_storage)

        try:
            # Executa a função da tarefa diretamente (ou via ImmediateBackend)
            generate_wedding_report_task.func(
                company_id=str(company.uuid),
                user_id=str(user.uuid),
                wedding_id=str(wedding.uuid),
                report_format="pdf",
            )

            # Verifica que uma notificação in-app foi gerada para o usuário
            notifications = list(
                Notification.objects.filter(
                    company=company,
                    user=user,
                    target_type="wedding",
                )
            )
            assert len(notifications) == 1
            notification = notifications[0]
            assert "Relatório Pronto para Download" in notification.title
            assert "https://r2.com/signed-report.pdf" in notification.link
            assert notification.wedding_id == wedding.uuid
        finally:
            ReportGenerationService._set_storage_service(None)

    def test_generate_wedding_report_task_excel_format(self) -> None:
        """Valida execução da task para formato Excel."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        mock_storage = MagicMock()
        mock_storage.upload_bytes.return_value = "reports/mock-saved.xlsx"
        mock_storage.generate_presigned_get_url.return_value = (
            "https://r2.com/signed-report.xlsx"
        )
        ReportGenerationService._set_storage_service(mock_storage)

        try:
            generate_wedding_report_task.func(
                company_id=company.pk,
                user_id=user.pk,
                wedding_id=str(wedding.uuid),
                report_format="excel",
            )

            notifications = list(
                Notification.objects.filter(
                    company=company,
                    user=user,
                    target_type="wedding",
                )
            )
            assert len(notifications) == 1
            assert "Excel" in notifications[0].message
        finally:
            ReportGenerationService._set_storage_service(None)
