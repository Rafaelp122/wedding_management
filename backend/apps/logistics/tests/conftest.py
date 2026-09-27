"""
Configuração Local de Testes: App Logistics.

Fornece fixtures parametrizáveis para criar contratos em qualquer estado,
hierarquias de aditivos e contratos com arquivos anexados.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from pytest_factoryboy import register

from apps.contracts.models import Contract
from apps.contracts.tests.factories import SupplierFactory
from apps.weddings.tests.factories import WeddingFactory

from .factories import ContractFactory, ItemFactory


register(SupplierFactory)
register(ContractFactory)
register(ItemFactory)


@pytest.fixture
def make_contract(user):
    """Factory fixture: cria contrato em qualquer status com wedding + supplier."""

    def _make(status=Contract.StatusChoices.DRAFT, **kwargs):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        if status in (Contract.StatusChoices.SIGNED, "SIGNED"):
            kwargs.setdefault("pdf_file", "contracts/dummy.pdf")
            kwargs.setdefault("signed_date", date.today())
            kwargs.setdefault("total_amount", Decimal("5000.00"))
        return ContractFactory(
            wedding=wedding, supplier=supplier, status=status, **kwargs
        )

    return _make


@pytest.fixture
def contract_with_file(user):
    """Contrato DRAFT com pdf_file válido salvo no storage."""
    wedding = WeddingFactory(company=user.company)
    supplier = SupplierFactory(company=user.company)
    contract = ContractFactory(wedding=wedding, supplier=supplier, pdf_file=None)
    contract.pdf_file = SimpleUploadedFile(
        "test.pdf", b"pdf content", content_type="application/pdf"
    )
    contract.save()
    return contract
