import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from apps.logistics.models import Contract
from apps.logistics.tests.factories import ContractFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestContractModel:
    """Testes de integridade do modelo Contract."""

    def test_contract_str(self):
        contract = ContractFactory(supplier__name="Buffet XPTO", total_amount=15000)
        assert "Buffet XPTO" in str(contract)
        assert "15000" in str(contract)

    def test_signed_contract_requires_pdf(self):
        """Regra local: Contrato assinado exige PDF."""
        contract = ContractFactory.build(
            status=Contract.StatusChoices.SIGNED,
            pdf_file=None,
            total_amount=1000,
            signed_date="2026-01-01",
        )
        with pytest.raises(ValidationError, match="exige o upload do arquivo PDF"):
            contract.clean()

    def test_signed_contract_requires_positive_amount(self):
        # Criamos um PDF mockado para passar na validação anterior
        fake_pdf = ContentFile(b"conteudo", name="contrato.pdf")
        contract = ContractFactory.build(
            status=Contract.StatusChoices.SIGNED,
            pdf_file=fake_pdf,
            total_amount=0,
            signed_date="2026-01-01",
        )
        with pytest.raises(ValidationError, match="deve ter um valor total positivo"):
            contract.clean()
