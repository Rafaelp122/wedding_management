from datetime import date
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import MaxFileSizeValidator
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


@pytest.mark.django_db
class TestContractFileValidation:
    """Testes de validação de tipo e tamanho do arquivo pdf_file."""

    def test_pdf_file_invalid_extension_fails(self, user):
        """Extensão inválida (exe) deve falhar validação."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        invalid_file = SimpleUploadedFile(
            name="malicious.exe",
            content=b"malicious content",
            content_type="application/octet-stream",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=invalid_file,
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert (
            "pdf_file" in str(exc_info.value)
            or "extensão" in str(exc_info.value).lower()
        )

    def test_pdf_file_exceeds_max_size_fails(self, user):
        """Arquivo > 10MB deve falhar validação."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        oversized_file = SimpleUploadedFile(
            name="big_file.pdf",
            content=b"0" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=oversized_file,
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert "10mb" in str(exc_info.value).lower()

    def test_pdf_file_valid_extension_passes(self, user):
        """Extensão válida (pdf) deve passar sem erro."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        valid_file = SimpleUploadedFile(
            name="contract.pdf",
            content=b"valid pdf content",
            content_type="application/pdf",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=valid_file,
        )
        contract.full_clean()

    def test_pdf_file_valid_png_passes(self, user):
        """Extensão válida (png) deve passar sem erro."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        valid_file = SimpleUploadedFile(
            name="signed_contract.png",
            content=b"valid png content",
            content_type="image/png",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=valid_file,
        )
        contract.full_clean()

    def test_pdf_file_valid_jpeg_passes(self, user):
        """Extensão válida (jpeg) deve passar sem erro."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        valid_file = SimpleUploadedFile(
            name="signed_contract.jpg",
            content=b"valid jpeg content",
            content_type="image/jpeg",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=valid_file,
        )
        contract.full_clean()

    def test_pdf_file_null_passes(self, user):
        """pdf_file nulo deve passar sem erro (campo opcional)."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test Contract",
            total_amount=Decimal("5000.00"),
            pdf_file=None,
        )
        contract.full_clean()


@pytest.mark.django_db
class TestContractPdfFileValidator:
    """Testes específicos para o MaxFileSizeValidator no campo pdf_file."""

    def test_validator_is_wired_on_field(self, user):
        """MaxFileSizeValidator deve estar configurado no campo pdf_file."""
        field = Contract._meta.get_field("pdf_file")

        validators = [
            v for v in field.validators if isinstance(v, MaxFileSizeValidator)
        ]
        assert len(validators) == 1
        assert validators[0].max_size == 10 * 1024 * 1024

    def test_oversized_file_raises_validation_error(self, user):
        """Arquivo acima de 10MB deve falhar na validação do campo."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        oversized = SimpleUploadedFile(
            name="big.pdf",
            content=b"0" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test",
            total_amount=Decimal("5000.00"),
            pdf_file=oversized,
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert "10MB" in str(exc_info.value)

    def test_signed_without_pdf_raises_validation_error(self, user):
        """Contrato SIGNED sem pdf_file deve falhar."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test",
            total_amount=Decimal("5000.00"),
            status=Contract.StatusChoices.SIGNED,
            pdf_file=None,
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert "ASSINADO" in str(exc_info.value) or "pdf" in str(exc_info.value).lower()

    def test_signed_without_total_amount_raises_validation_error(self, user):
        """Contrato SIGNED sem total_amount deve falhar."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        valid_file = SimpleUploadedFile(
            name="contract.pdf",
            content=b"pdf content",
            content_type="application/pdf",
        )
        contract = Contract(
            company=user.company,
            wedding=wedding,
            supplier=supplier,
            name="Test",
            status=Contract.StatusChoices.SIGNED,
            total_amount=Decimal("0.00"),
            pdf_file=valid_file,
        )

        with pytest.raises(ValidationError) as exc_info:
            contract.full_clean()

        assert "valor" in str(exc_info.value).lower()
