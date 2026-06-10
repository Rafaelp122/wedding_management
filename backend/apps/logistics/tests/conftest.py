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

from apps.logistics.models import Contract
from apps.weddings.tests.factories import WeddingFactory

from .factories import ContractFactory, ItemFactory, SupplierFactory


register(SupplierFactory)
register(ContractFactory)
register(ItemFactory)


@pytest.fixture
def make_contract(user):
    """Factory fixture: cria contrato em qualquer status com wedding + supplier."""

    def _make(status=Contract.StatusChoices.DRAFT, **kwargs):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        return ContractFactory(
            wedding=wedding, supplier=supplier, status=status, **kwargs
        )

    return _make


@pytest.fixture
def contract_with_addendum(user):
    """Contrato pai SIGNED com um aditivo DRAFT vinculado."""
    parent = ContractFactory(
        wedding__company=user.company,
        status="SIGNED",
        total_amount=Decimal("5000.00"),
        signed_date=date.today(),
        pdf_file="contracts/dummy.pdf",
    )
    addendum = ContractFactory(
        wedding=parent.wedding,
        supplier=parent.supplier,
        parent=parent,
        status="DRAFT",
        total_amount=Decimal("1000.00"),
    )
    return parent, addendum


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
