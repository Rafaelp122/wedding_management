from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.logistics.models import Contract
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestContractModelMetadata:
    """Testes de representação e metadados do modelo Contract."""

    def test_contract_str_contains_supplier_and_wedding(self, user):
        """__str__ deve conter supplier, wedding e total_amount."""
        wedding = WeddingFactory(user_context=user, bride_name="Ana", groom_name="João")
        supplier = SupplierFactory(company=user.company, name="Buffet Premium")
        contract = ContractFactory(
            wedding=wedding,
            supplier=supplier,
            total_amount=Decimal("15000.00"),
        )

        result = str(contract)
        assert "Buffet Premium" in result
        assert "Ana" in result
        assert "João" in result
        assert "15000.00" in result

    def test_contract_ordering_by_created_at_descending(self, user):
        """Ordenação padrão deve ser por -created_at."""
        wedding = WeddingFactory(user_context=user)
        c1 = ContractFactory(wedding=wedding, description="Contrato Antigo")
        c2 = ContractFactory(wedding=wedding, description="Contrato Novo")

        contracts = list(Contract.objects.all())
        assert contracts[0] == c2
        assert contracts[1] == c1

    def test_contract_status_default_is_draft(self, user):
        """Status padrão deve ser DRAFT."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding)
        assert contract.status == Contract.StatusChoices.DRAFT


@pytest.mark.django_db
class TestContractSignedValidation:
    """Testes da regra BR-L01: contrato ASSINADO exige PDF, valor positivo e data."""

    def test_signed_without_pdf_fails(self, user):
        """Contrato ASSINADO sem PDF deve falhar validação."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            status=Contract.StatusChoices.SIGNED,
            total_amount=Decimal("5000.00"),
            signed_date=date.today(),
            pdf_file="",
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert "PDF" in str(exc_info.value).upper()

    def test_signed_without_positive_amount_fails(self, user):
        """Contrato ASSINADO com valor zero ou negativo deve falhar.
        As validações acumulam — PDF também será exigido, mas valor pega também."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            status=Contract.StatusChoices.SIGNED,
            total_amount=Decimal("0.00"),
            signed_date=date.today(),
            pdf_file="",
        )

        with pytest.raises(ValidationError):
            contract.full_clean()

    def test_signed_without_signed_date_fails(self, user):
        """Contrato ASSINADO sem signed_date deve falhar."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            status=Contract.StatusChoices.SIGNED,
            total_amount=Decimal("5000.00"),
            signed_date=None,
            pdf_file="",
        )

        with pytest.raises(ValidationError):
            contract.full_clean()

    def test_draft_passes_without_requirements(self, user):
        """Contrato DRAFT não exige PDF, valor ou assinatura."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, status=Contract.StatusChoices.DRAFT)
        contract.full_clean()

    def test_pending_passes_without_requirements(self, user):
        """Contrato PENDING não exige PDF, valor ou assinatura."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(
            wedding=wedding,
            status=Contract.StatusChoices.PENDING,
        )
        contract.full_clean()
