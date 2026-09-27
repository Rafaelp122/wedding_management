"""
Testes de integridade, invariantes e ciclo de vida de Contract e ContractAddendum.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.tests.factories import (
    ContractAddendumFactory as _ContractAddendumFactory,
)
from apps.contracts.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.contracts.tests.factories import (
    SignedContractFactory as _SignedContractFactory,
)
from apps.contracts.tests.factories import SupplierFactory as _SupplierFactory
from apps.core.exceptions import BusinessRuleViolation
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def SignedContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _SignedContractFactory(*args, **kwargs))


def ContractAddendumFactory(*args: Any, **kwargs: Any) -> ContractAddendum:
    return cast(ContractAddendum, _ContractAddendumFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Any:
    return _SupplierFactory(*args, **kwargs)


def CompanyFactory(*args: Any, **kwargs: Any) -> Any:
    return _CompanyFactory(*args, **kwargs)


def WeddingFactory(*args: Any, **kwargs: Any) -> Any:
    return _WeddingFactory(*args, **kwargs)


@pytest.mark.django_db
class TestContractModel:
    """Testes unitários de regras de domínio do modelo Contract."""

    @pytest.mark.skip(reason="Obsolete due to Phase 2 refactoring")
    def test_supplier_contract_defaults(self, user: Any) -> None:
        """Contrato de fornecedor é criado com valores padrão esperados."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.SUPPLIER,
            total_amount=Decimal("5000.00"),
        )

        assert contract.status == Contract.StatusChoices.DRAFT
        assert contract.contract_type == Contract.ContractTypeChoices.SUPPLIER
        assert contract.supplier is not None
        assert contract.service_tier is None
        assert contract.total_amount == Decimal("5000.00")
        assert contract.base_amount == Decimal("5000.00")
        assert contract.effective_amount == Decimal("5000.00")
        assert contract.addendums_total == Decimal("0.00")
        assert not contract.has_file
        assert contract.has_file is False
        assert contract.file_name is None

    def test_planner_contract_defaults(self, user: Any) -> None:
        """Contrato de assessoria (PLANNER) é criado com valores esperados."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            service_tier=Contract.ServiceTierChoices.COMPLETA,
            total_amount=Decimal("6000.00"),
            installments_count=3,
        )

        assert contract.status == Contract.StatusChoices.DRAFT
        assert contract.contract_type == Contract.ContractTypeChoices.PLANNER
        assert contract.supplier is None
        assert contract.service_tier == Contract.ServiceTierChoices.COMPLETA
        assert contract.total_amount == Decimal("6000.00")
        assert contract.effective_amount == Decimal("6000.00")
        assert contract.installments_count == 3
        assert "Contrato de Assessoria" in str(contract)

    def test_supplier_contract_requires_supplier(self, user: Any) -> None:
        """Contrato do tipo SUPPLIER sem fornecedor é rejeitado pelo clean()."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.SUPPLIER,
            supplier=None,
            name="Buffet Teste",
            total_amount=Decimal("1000.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "supplier" in excinfo.value.message_dict

    def test_planner_contract_cannot_have_supplier(self, user: Any) -> None:
        """Contrato do tipo PLANNER não pode possuir fornecedor vinculado."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            supplier=supplier,
            service_tier=Contract.ServiceTierChoices.COMPLETA,
            name="Assessoria VIP",
            total_amount=Decimal("5000.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "supplier" in excinfo.value.message_dict

    def test_planner_contract_requires_service_tier(self, user: Any) -> None:
        """Contrato do tipo PLANNER exige especificação do service_tier."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            supplier=None,
            service_tier=None,
            name="Assessoria Sem Tier",
            total_amount=Decimal("5000.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "service_tier" in excinfo.value.message_dict

    def test_contract_clean_negative_amount(self, user: Any) -> None:
        """Valores negativos são rejeitados tanto para fornecedor quanto assessoria."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            service_tier=Contract.ServiceTierChoices.PARCIAL,
            total_amount=Decimal("-10.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "total_amount" in excinfo.value.message_dict

    def test_contract_clean_zero_installments(self, user: Any) -> None:
        """Número de parcelas menor que 1 é rejeitado."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            service_tier=Contract.ServiceTierChoices.FINAL,
            total_amount=Decimal("2000.00"),
            installments_count=0,
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "installments_count" in excinfo.value.message_dict

    def test_signed_contract_requires_signed_date(self, user: Any) -> None:
        """Contrato com status SIGNED exige signed_date."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            service_tier=Contract.ServiceTierChoices.COMPLETA,
            total_amount=Decimal("5000.00"),
            status=Contract.StatusChoices.SIGNED,
            signed_date=None,
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "signed_date" in excinfo.value.message_dict

    def test_signed_supplier_contract_requires_pdf_file(self, user: Any) -> None:
        """Contrato de fornecedor marcado como SIGNED exige anexo de arquivo."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        supplier = SupplierFactory(company=user.company)
        contract = Contract(
            company=user.company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.SUPPLIER,
            supplier=supplier,
            name="Decoração",
            total_amount=Decimal("5000.00"),
            status=Contract.StatusChoices.SIGNED,
            signed_date=dt.date.today(),
            pdf_file=None,
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "PDF" in str(excinfo.value).upper()

    def test_contract_cross_tenant_supplier_isolation(self) -> None:
        """Impedir vincular fornecedor de outra organização."""
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_a = WeddingFactory(company=company_a)
        supplier_b = SupplierFactory(company=company_b)

        contract = Contract(
            company=company_a,
            wedding=wedding_a,
            contract_type=Contract.ContractTypeChoices.SUPPLIER,
            supplier=supplier_b,
            name="Contrato Cruzado",
            total_amount=Decimal("3000.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "supplier" in excinfo.value.message_dict

    def test_contract_cross_tenant_wedding_isolation(self) -> None:
        """Impedir vincular casamento de outra organização."""
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_b = WeddingFactory(company=company_b)

        contract = Contract(
            company=company_a,
            wedding=wedding_b,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            service_tier=Contract.ServiceTierChoices.COMPLETA,
            name="Contrato Cruzado",
            total_amount=Decimal("3000.00"),
        )
        with pytest.raises(ValidationError) as excinfo:
            contract.clean()
        assert "wedding" in excinfo.value.message_dict

    def test_contract_lifecycle_sign_and_cancel(self, user: Any) -> None:
        """Ciclo de vida do contrato: transições sign() e cancel()."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        today = dt.date.today()
        contract.sign(signed_date=today)
        assert contract.status == Contract.StatusChoices.SIGNED
        assert contract.signed_date == today

        contract.cancel()
        assert contract.status == Contract.StatusChoices.CANCELED

        with pytest.raises(BusinessRuleViolation):
            contract.sign()

    def test_contract_file_attachment(self, user: Any) -> None:
        """Anexo e desanexo de arquivos no contrato."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        file = SimpleUploadedFile(
            "contrato.pdf", b"dummy pdf content", content_type="application/pdf"
        )
        contract.attach_file(file)
        assert contract.has_file
        assert "contrato" in (contract.file_name or "")

        contract.detach_file()
        assert not contract.has_file


@pytest.mark.django_db
class TestContractAddendumModel:
    """Testes unitários de regras de domínio do modelo ContractAddendum."""

    def test_addendum_linked_to_supplier_contract(self, user: Any) -> None:
        """Termo aditivo vinculado a contrato de fornecedor é criado com sucesso."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        addendum = ContractAddendumFactory(
            contract=contract,
            amount=Decimal("1200.00"),
            justification="Acréscimo de 50 cadeiras",
        )

        assert addendum.status == ContractAddendum.StatusChoices.PENDING
        assert addendum.amount == Decimal("1200.00")
        assert addendum.wedding == wedding
        assert addendum.company == user.company

    def test_addendum_linked_to_planner_contract(self, user: Any) -> None:
        """TESTE OBRIGATÓRIO: Termo aditivo vinculado a contrato de ASSESSORIA (PLANNER)."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        planner_contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            service_tier=Contract.ServiceTierChoices.COMPLETA,
            total_amount=Decimal("8000.00"),
        )

        addendum = ContractAddendumFactory(
            contract=planner_contract,
            amount=Decimal("2000.00"),
            justification="Extensão da assessoria para pós-evento (almoço de recepção)",
        )

        assert addendum.contract == planner_contract
        assert addendum.contract.contract_type == Contract.ContractTypeChoices.PLANNER
        assert addendum.amount == Decimal("2000.00")
        assert addendum.wedding == wedding
        assert addendum.company == user.company

        # Formaliza a assinatura do aditivo do contrato de assessoria
        addendum.sign(signed_date=dt.date.today())
        addendum.save()

        assert addendum.status == ContractAddendum.StatusChoices.SIGNED
        assert planner_contract.addendums_total == Decimal("2000.00")
        assert planner_contract.effective_amount == Decimal("10000.00")

    def test_addendum_clean_negative_or_zero_amount(self, user: Any) -> None:
        """Aditivo com montante zero ou negativo é rejeitado."""
        contract = ContractFactory()
        addendum = ContractAddendum(
            company=contract.company,
            wedding=contract.wedding,
            contract=contract,
            amount=Decimal("0.00"),
            justification="Valor zero",
        )
        with pytest.raises(ValidationError) as excinfo:
            addendum.clean()
        assert "amount" in excinfo.value.message_dict

    def test_addendum_clean_empty_justification(self, user: Any) -> None:
        """Justificativa vazia ou composta apenas de espaços é rejeitada."""
        contract = ContractFactory()
        addendum = ContractAddendum(
            company=contract.company,
            wedding=contract.wedding,
            contract=contract,
            amount=Decimal("500.00"),
            justification="   ",
        )
        with pytest.raises(ValidationError) as excinfo:
            addendum.clean()
        assert "justification" in excinfo.value.message_dict

    def test_addendum_cross_wedding_mismatch(self) -> None:
        """Termo aditivo não pode apontar para casamento diferente do contrato principal."""
        company = CompanyFactory()
        wedding_1 = WeddingFactory(company=company)
        wedding_2 = WeddingFactory(company=company)
        contract = ContractFactory(company=company, wedding=wedding_1)

        addendum = ContractAddendum(
            company=company,
            wedding=wedding_2,
            contract=contract,
            amount=Decimal("500.00"),
            justification="Mismatch de casamento",
        )
        with pytest.raises(ValidationError) as excinfo:
            addendum.clean()
        assert (
            "wedding" in excinfo.value.message_dict
            or "contract" in excinfo.value.message_dict
        )

    def test_addendum_lifecycle_sign_and_cancel(self, user: Any) -> None:
        """Ciclo de vida do termo aditivo com assinatura e cancelamento."""
        contract = ContractFactory()
        addendum = ContractAddendumFactory(contract=contract)

        assert addendum.status == ContractAddendum.StatusChoices.PENDING
        addendum.sign()
        assert addendum.status == ContractAddendum.StatusChoices.SIGNED
        assert addendum.signed_date is not None

        addendum.cancel()
        assert addendum.status == ContractAddendum.StatusChoices.CANCELED

        with pytest.raises(BusinessRuleViolation):
            addendum.sign()
