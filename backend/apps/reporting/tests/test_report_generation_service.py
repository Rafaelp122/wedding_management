"""
Testes unitários para o ReportGenerationService (geração de PDF, Excel e Storage).
"""

from datetime import date
from decimal import Decimal
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import (
    BudgetFactory as _BudgetFactory,
)
from apps.finances.tests.factories import (
    ExpenseFactory as _ExpenseFactory,
)
from apps.finances.tests.factories import (
    InstallmentFactory as _InstallmentFactory,
)
from apps.logistics.models import Contract
from apps.logistics.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.logistics.tests.factories import (
    SupplierFactory as _SupplierFactory,
)
from apps.reporting.services import ReportGenerationService
from apps.scheduler.tests.factories import TaskFactory as _TaskFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestReportGenerationService:
    """Suíte de testes para geração de relatórios consolidados em PDF e Excel."""

    def test_generate_wedding_pdf_success(self) -> None:
        """Gera PDF com sucesso para casamento populado e valida %PDF-."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        budget = _BudgetFactory(
            company=company,
            wedding=wedding,
            total_estimated=Decimal("50000.00"),
        )
        cat = _BudgetCategoryFactory(
            company=company, budget=budget, allocated_budget=Decimal("20000.00")
        )
        expense = _ExpenseFactory(company=company, category=cat, wedding=wedding)
        _InstallmentFactory(
            company=company,
            expense=expense,
            wedding=wedding,
            amount=Decimal("5000.00"),
            paid_date=date(2026, 1, 15),
            status=Installment.StatusChoices.PAID,
        )
        _InstallmentFactory(
            company=company,
            expense=expense,
            wedding=wedding,
            amount=Decimal("5000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        supplier = _SupplierFactory(company=company)
        _ContractFactory(
            company=company,
            wedding=wedding,
            supplier=supplier,
            total_amount=Decimal("10000.00"),
            status=Contract.StatusChoices.SIGNED,
            signed_date=date(2026, 1, 10),
            pdf_file="contracts/dummy.pdf",
        )
        _TaskFactory(company=company, wedding=wedding, is_completed=True)
        _TaskFactory(company=company, wedding=wedding, is_completed=False)

        pdf_bytes = ReportGenerationService.generate_wedding_pdf(
            company=company,
            wedding_uuid=wedding.uuid,
        )

        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF-")

    def test_generate_wedding_pdf_empty_wedding(self) -> None:
        """Gera PDF consistente para casamento recém-criado sem finanças."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        pdf_bytes = ReportGenerationService.generate_wedding_pdf(
            company=company,
            wedding_uuid=wedding.uuid,
        )

        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b"%PDF-")

    def test_generate_wedding_excel_success(self) -> None:
        """Gera Excel (.xlsx) com sucesso e valida assinatura binária PK zip."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        budget = _BudgetFactory(
            company=company,
            wedding=wedding,
            total_estimated=Decimal("80000.00"),
        )
        cat = _BudgetCategoryFactory(
            company=company, budget=budget, allocated_budget=Decimal("30000.00")
        )
        expense = _ExpenseFactory(company=company, category=cat, wedding=wedding)
        _InstallmentFactory(
            company=company,
            expense=expense,
            wedding=wedding,
            amount=Decimal("10000.00"),
            paid_date=date(2026, 1, 15),
            status=Installment.StatusChoices.PAID,
        )

        excel_bytes = ReportGenerationService.generate_wedding_excel(
            company=company,
            wedding_uuid=wedding.uuid,
        )

        assert isinstance(excel_bytes, bytes)
        assert len(excel_bytes) > 0
        # Assinatura mágica de arquivos ZIP / XLSX
        assert excel_bytes.startswith(b"PK\x03\x04")

    def test_generate_wedding_report_rejects_cross_tenant(self) -> None:
        """Rejeita geração de relatório para casamento pertencente a outro tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            ReportGenerationService.generate_wedding_pdf(
                company=user_a.company,
                wedding_uuid=wedding_b.uuid,
            )

        with pytest.raises(ObjectNotFoundError):
            ReportGenerationService.generate_wedding_excel(
                company=user_a.company,
                wedding_uuid=wedding_b.uuid,
            )

    def test_generate_and_store_report_storage_integration(self) -> None:
        """Valida que generate_and_store_report envia bytes ao StorageService."""
        user = UserFactory()
        company = user.company
        wedding = WeddingFactory(company=company)

        mock_storage = MagicMock()
        mock_storage.upload_bytes.return_value = "reports/mock-key.pdf"
        mock_storage.generate_presigned_get_url.return_value = (
            "https://r2.com/download.pdf"
        )

        ReportGenerationService._set_storage_service(mock_storage)
        try:
            key, url = ReportGenerationService.generate_and_store_report(
                company=company,
                wedding_uuid=wedding.uuid,
                report_format="pdf",
            )

            assert key == "reports/mock-key.pdf"
            assert url == "https://r2.com/download.pdf"
            mock_storage.upload_bytes.assert_called_once()
            mock_storage.generate_presigned_get_url.assert_called_once_with(
                bucket="wedding-reports",
                object_key="reports/mock-key.pdf",
                expires_in=3600,
            )
        finally:
            ReportGenerationService._set_storage_service(None)
