from datetime import date
from decimal import Decimal
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.core.validators import MaxFileSizeValidator
from apps.logistics.models import Contract, Supplier
from apps.logistics.tests.factories import ContractFactory as _ContractFactory
from apps.logistics.tests.factories import SupplierFactory as _SupplierFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestContractModelMetadata:
    """Testes de representação e metadados do modelo Contract."""

    def test_contract_str_contains_supplier_and_wedding(self, user: Any) -> None:
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

    def test_contract_ordering_by_created_at_descending(self, user: Any) -> None:
        """Ordenação padrão deve ser por -created_at."""
        wedding = WeddingFactory(user_context=user)
        c1 = ContractFactory(wedding=wedding, description="Contrato Antigo")
        c2 = ContractFactory(wedding=wedding, description="Contrato Novo")

        contracts = list(Contract.objects.all())
        assert contracts[0] == c2
        assert contracts[1] == c1

    def test_contract_status_default_is_draft(self, user: Any) -> None:
        """Status padrão deve ser DRAFT."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding)
        assert contract.status == Contract.StatusChoices.DRAFT


@pytest.mark.django_db
class TestContractSignedValidation:
    """Testes da regra BR-L01: contrato ASSINADO exige PDF, valor positivo e data."""

    def test_signed_without_pdf_fails(self, user: Any) -> None:
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

    def test_signed_without_positive_amount_fails(self, user: Any) -> None:
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

    def test_signed_without_signed_date_fails(self, user: Any) -> None:
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

    def test_draft_passes_without_requirements(self, user: Any) -> None:
        """Contrato DRAFT não exige PDF, valor ou assinatura."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, status=Contract.StatusChoices.DRAFT)
        contract.full_clean()

    def test_pending_passes_without_requirements(self, user: Any) -> None:
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

    def test_pdf_file_invalid_extension_fails(self, user: Any) -> None:
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

    def test_pdf_file_exceeds_max_size_fails(self, user: Any) -> None:
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

    def test_pdf_file_valid_extension_passes(self, user: Any) -> None:
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

    def test_pdf_file_valid_png_passes(self, user: Any) -> None:
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

    def test_pdf_file_valid_jpeg_passes(self, user: Any) -> None:
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

    def test_pdf_file_null_passes(self, user: Any) -> None:
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

    def test_max_file_size_validator_is_wired_on_field(self, user: Any) -> None:
        """MaxFileSizeValidator deve estar configurado no campo pdf_file."""
        field = Contract._meta.get_field("pdf_file")

        validators = [
            v for v in field.validators if isinstance(v, MaxFileSizeValidator)
        ]
        assert len(validators) == 1
        assert validators[0].max_size == 10 * 1024 * 1024


@pytest.mark.django_db
class TestContractStatusTransitionValidation:
    """Testes da máquina de estados de contrato em Contract.clean()."""

    _SIGNED_KWARGS = {
        "pdf_file": "contracts/dummy.pdf",
        "signed_date": date.today(),
        "total_amount": Decimal("5000.00"),
    }

    _VALID: list[tuple[str, str, dict[str, object]]] = [
        ("DRAFT", "PENDING", {}),
        ("DRAFT", "CANCELED", {}),
        ("PENDING", "SIGNED", {}),
        ("PENDING", "DRAFT", {}),
        ("PENDING", "CANCELED", {}),
        ("SIGNED", "CANCELED", _SIGNED_KWARGS),
        ("CANCELED", "DRAFT", {}),
    ]

    _INVALID: list[tuple[str, str, dict[str, object]]] = [
        ("DRAFT", "SIGNED", {}),
        ("SIGNED", "DRAFT", _SIGNED_KWARGS),
        ("CANCELED", "SIGNED", {}),
        ("CANCELED", "PENDING", {}),
    ]

    @pytest.mark.parametrize("from_status, to_status, kwargs", _VALID)
    def test_valid_transitions(
        self, make_contract: Any, from_status: Any, to_status: Any, kwargs: Any
    ) -> None:
        contract = make_contract(from_status, **kwargs)
        if to_status == "SIGNED":
            contract.pdf_file = "contracts/test.pdf"
            contract.signed_date = date.today()
            contract.total_amount = Decimal("5000.00")
        contract.status = to_status
        contract.full_clean()

    @pytest.mark.parametrize("from_status, to_status, kwargs", _INVALID)
    def test_invalid_transitions(
        self, make_contract: Any, from_status: Any, to_status: Any, kwargs: Any
    ) -> None:
        contract = make_contract(from_status, **kwargs)
        contract.status = to_status
        with pytest.raises(ValidationError):
            contract.full_clean()

    def test_new_instance_not_validated_as_transition(self) -> None:
        """Criação direta de contrato ASSINADO não deve falhar por transição,
        apenas pelas regras de SIGNED (PDF, valor, data)."""
        with pytest.raises(ValidationError) as exc_info:
            Contract(
                company=None,
                wedding=None,
                supplier=None,
                status="SIGNED",
                total_amount=Decimal("5000.00"),
            ).full_clean()
        errors = str(exc_info.value)
        assert "PDF" in errors.upper() or "data" in errors.lower()
        assert "transitar" not in errors


@pytest.mark.django_db
class TestContractHierarchyValidation:
    """Testes de validação de integridade da hierarquia e termos aditivos."""

    def test_contract_self_parent_fails(self, user: Any) -> None:
        """Um contrato não pode ser pai de si mesmo."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)
        contract.parent = contract

        with pytest.raises(ValidationError) as exc_info:
            contract.clean()

        assert "não pode ser pai de si mesmo" in str(exc_info.value)

    def test_contract_cross_wedding_parent_fails(self, user: Any) -> None:
        """Contrato pai deve pertencer ao mesmo casamento."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        parent = ContractFactory(wedding=wedding1, company=user.company)
        child = ContractFactory(wedding=wedding2, company=user.company)
        child.parent = parent

        with pytest.raises(ValidationError) as exc_info:
            child.clean()

        assert "outro casamento" in str(exc_info.value)

    def test_contract_circular_parent_fails(self, user: Any) -> None:
        """Cadeia circular de parentesco é bloqueada."""
        wedding = WeddingFactory(user_context=user)
        c1 = ContractFactory(wedding=wedding, company=user.company)
        c2 = ContractFactory(wedding=wedding, company=user.company, parent=c1)
        c3 = ContractFactory(wedding=wedding, company=user.company, parent=c2)

        c1.parent = c3
        with pytest.raises(ValidationError) as exc_info:
            c1.clean()

        assert "descendente" in str(exc_info.value)

    def test_contract_valid_parent_passes(self, user: Any) -> None:
        """Vínculo de aditivo válido com pai do mesmo casamento passa com sucesso."""
        wedding = WeddingFactory(user_context=user)
        parent = ContractFactory(wedding=wedding, company=user.company)
        child = ContractFactory(wedding=wedding, company=user.company, parent=parent)
        child.clean()

    def test_unsaved_contract_with_parent_passes(self, user: Any) -> None:
        """Contrato novo (sem pk) com pai válido passa na validação."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        parent = ContractFactory(
            wedding=wedding, company=user.company, supplier=supplier
        )
        new_contract = Contract(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            parent=parent,
            total_amount=Decimal("1000.00"),
            status=Contract.StatusChoices.DRAFT,
        )
        new_contract.clean()
