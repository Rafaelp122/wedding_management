"""
Testes de serviços de aplicação para ContractService e ContractAddendumService.
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Any, cast

import pytest

from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.schemas import (
    ContractAddendumIn,
    ContractAddendumSignIn,
    ContractFullCreateIn,
    ContractIn,
    ContractItemIn,
    ContractPatchIn,
)
from apps.contracts.services import ContractAddendumService, ContractService
from apps.contracts.tests.factories import (
    ContractAddendumFactory as _ContractAddendumFactory,
)
from apps.contracts.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.contracts.tests.factories import SupplierFactory as _SupplierFactory
from apps.core.exceptions import BusinessRuleViolation
from apps.finances.models import Budget, BudgetCategory, Expense
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ContractAddendumFactory(*args: Any, **kwargs: Any) -> ContractAddendum:
    return cast(ContractAddendum, _ContractAddendumFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Any:
    return _SupplierFactory(*args, **kwargs)


def ClientFactory(*args: Any, **kwargs: Any) -> Any:
    return _ClientFactory(*args, **kwargs)


def WeddingFactory(*args: Any, **kwargs: Any) -> Any:
    return _WeddingFactory(*args, **kwargs)


@pytest.mark.django_db
class TestContractService:
    """Testes dos métodos de escrita e orquestração de ContractService."""

    def test_create_supplier_contract(self, user: Any) -> None:
        """Criação básica de contrato de fornecedor."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        supplier = SupplierFactory(company=user.company)

        payload = ContractIn(
            wedding=wedding.uuid,
            supplier=supplier.uuid,
            contract_type="SUPPLIER",
            name="Fotografia",
            total_amount=Decimal("4500.00"),
            description="Cobertura de cerimônia e festa",
        )

        contract = ContractService.create(company=user.company, payload=payload)

        assert contract.pk is not None
        assert contract.company == user.company
        assert contract.wedding == wedding
        assert contract.supplier == supplier
        assert contract.total_amount == Decimal("4500.00")
        assert contract.contract_type == "SUPPLIER"

    def test_create_planner_contract(self, user: Any) -> None:
        """Criação de contrato de assessoria via ContractService."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        client = ClientFactory(company=user.company)

        payload = ContractIn(
            wedding=wedding.uuid,
            contract_type="PLANNER",
            service_tier="COMPLETA",
            client=client.uuid,
            name="Assessoria Master",
            total_amount=Decimal("7000.00"),
            installments_count=4,
        )

        contract = ContractService.create(company=user.company, payload=payload)

        assert contract.pk is not None
        assert contract.contract_type == "PLANNER"
        assert contract.service_tier == "COMPLETA"
        assert contract.supplier is None
        assert contract.client == client
        assert contract.total_amount == Decimal("7000.00")
        assert contract.installments_count == 4

    def test_create_full_with_items_and_expense(self, user: Any) -> None:
        """Criação atômica de contrato, itens e despesa vinculada."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        supplier = SupplierFactory(company=user.company)
        budget = cast(Budget, BudgetFactory(company=user.company, wedding=wedding))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=user.company, budget=budget, wedding=wedding),
        )

        payload = ContractFullCreateIn(
            wedding=wedding.uuid,
            supplier=supplier.uuid,
            name="Locação de Mobiliário",
            total_amount=Decimal("3000.00"),
            items=[
                ContractItemIn(name="Mesa Redonda", quantity=20),
                ContractItemIn(name="Cadeira Dior", quantity=160),
            ],
            create_expense=True,
            expense_category=category.uuid,
            expense_num_installments=2,
            expense_first_due_date=dt.date.today(),
        )

        contract = ContractService.create_full_from_payload(
            company=user.company, payload=payload
        )

        assert contract.pk is not None
        assert contract.items.count() == 2
        assert Expense.objects.filter(company=user.company, contract=contract).exists()

    def test_update_contract(self, user: Any) -> None:
        """Atualização parcial dos campos de um contrato."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        patch_payload = ContractPatchIn(
            name="Novo Nome Atualizado",
            total_amount=Decimal("6000.00"),
        )
        updated = ContractService.update(
            company=user.company, instance=contract, payload=patch_payload
        )

        assert updated.name == "Novo Nome Atualizado"
        assert updated.total_amount == Decimal("6000.00")

    def test_update_rejects_locked_status_and_type(self, user: Any) -> None:
        """Status e tipo exigem endpoints dedicados (422 via envelope)."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        with pytest.raises(BusinessRuleViolation) as excinfo:
            ContractService.update(
                company=user.company,
                instance=contract,
                payload=ContractPatchIn(status="SIGNED"),
            )
        assert excinfo.value.code == "contract_locked_field_update"

        with pytest.raises(BusinessRuleViolation) as excinfo:
            ContractService.update(
                company=user.company,
                instance=contract,
                payload=ContractPatchIn(contract_type="SUPPLIER"),
            )
        assert excinfo.value.code == "contract_locked_field_update"

    def test_update_rejects_total_amount_when_signed(self, user: Any) -> None:
        """Valor de contrato assinado só muda via aditivo."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)
        contract.sign(signed_date=dt.date.today())
        contract.save()

        with pytest.raises(BusinessRuleViolation) as excinfo:
            ContractService.update(
                company=user.company,
                instance=contract,
                payload=ContractPatchIn(total_amount=Decimal("9999.00")),
            )
        assert excinfo.value.code == "contract_signed_value_locked"

    def test_sign_persists_auto_signed_date(self, user: Any) -> None:
        """Assinatura sem data preenche e persiste a data de hoje."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        signed = ContractService.sign(company=user.company, instance=contract)
        assert signed.signed_date == dt.date.today()

        signed.refresh_from_db()
        assert signed.signed_date == dt.date.today()
        assert signed.status == Contract.StatusChoices.SIGNED

    def test_cannot_delete_signed_contract(self, user: Any) -> None:
        """Contrato formalmente assinado não pode ser excluído."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            status=Contract.StatusChoices.PENDING,
        )

        # Formaliza a assinatura
        contract.sign(signed_date=dt.date.today(), pdf_file="dummy.pdf")
        contract.save()

        with pytest.raises(BusinessRuleViolation) as excinfo:
            ContractService.delete(company=user.company, instance=contract)
        assert "não é possível excluir" in str(excinfo.value).lower()


@pytest.mark.django_db
class TestContractAddendumService:
    """Testes dos métodos de ContractAddendumService."""

    def test_create_and_sign_addendum_for_supplier_contract(self, user: Any) -> None:
        """Criação e assinatura de aditivo com atualização de despesa em fornecedor."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("5000.00"),
        )

        # Cria despesa associada
        budget = cast(Budget, BudgetFactory(company=user.company, wedding=wedding))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=user.company, budget=budget, wedding=wedding),
        )
        expense = cast(
            Expense,
            ExpenseFactory(
                company=user.company,
                wedding=wedding,
                category=category,
                contract=contract,
                name="Despesa Contrato Fornecedor",
                estimated_amount=Decimal("5000.00"),
                actual_amount=Decimal("5000.00"),
            ),
        )
        InstallmentFactory(
            company=user.company,
            expense=expense,
            amount=Decimal("5000.00"),
            installment_number=1,
            due_date=dt.date.today(),
        )

        payload = ContractAddendumIn(
            amount=Decimal("1500.00"),
            justification="Acréscimo de serviços",
            signed_date=dt.date.today(),
        )

        addendum = ContractAddendumService.create(
            company=user.company,
            contract_id=contract.uuid,
            payload=payload,
        )

        assert addendum.status == ContractAddendum.StatusChoices.PENDING

        signed_addendum = ContractAddendumService.sign(
            company=user.company,
            contract_id=contract.uuid,
            addendum_id=addendum.uuid,
            payload=ContractAddendumSignIn(signed_date=dt.date.today()),
        )

        assert signed_addendum.status == ContractAddendum.StatusChoices.SIGNED
        expense.refresh_from_db()
        assert expense.actual_amount == Decimal("6500.00")

    def test_create_and_sign_addendum_for_planner_contract(self, user: Any) -> None:
        """TESTE OBRIGATÓRIO: Criação e assinatura de aditivo em contrato de ASSESSORIA (PLANNER).

        Valida que o aditivo em contrato de assessoria reflete na despesa de honorários.
        """
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        planner_contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("8000.00"),
            service_tier=Contract.ServiceTierChoices.COMPLETA,
        )

        budget = cast(Budget, BudgetFactory(company=user.company, wedding=wedding))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=user.company, budget=budget, wedding=wedding),
        )
        planner_expense = cast(
            Expense,
            ExpenseFactory(
                company=user.company,
                wedding=wedding,
                category=category,
                contract=planner_contract,
                name="Honorários de Assessoria",
                estimated_amount=Decimal("8000.00"),
                actual_amount=Decimal("8000.00"),
            ),
        )
        InstallmentFactory(
            company=user.company,
            expense=planner_expense,
            amount=Decimal("8000.00"),
            installment_number=1,
            due_date=dt.date.today(),
        )

        addendum_payload = ContractAddendumIn(
            amount=Decimal("2500.00"),
            justification="Consultoria extra para escolha de vestidos e padrinhos",
        )

        addendum = ContractAddendumService.create(
            company=user.company,
            contract_id=planner_contract.uuid,
            payload=addendum_payload,
        )
        assert addendum.status == ContractAddendum.StatusChoices.PENDING

        signed_addendum = ContractAddendumService.sign(
            company=user.company,
            contract_id=planner_contract.uuid,
            addendum_id=addendum.uuid,
            payload=ContractAddendumSignIn(signed_date=dt.date.today()),
        )

        assert signed_addendum.status == ContractAddendum.StatusChoices.SIGNED
        planner_expense.refresh_from_db()
        assert planner_expense.actual_amount == Decimal("10500.00")
        assert planner_contract.effective_amount == Decimal("10500.00")

    def test_cancel_and_delete_addendum(self, user: Any) -> None:
        """Cancelamento e exclusão de termo aditivo pendente."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)
        addendum = ContractAddendumFactory(
            contract=contract,
            company=user.company,
            wedding=wedding,
        )

        canceled = ContractAddendumService.cancel(
            company=user.company,
            contract_id=contract.uuid,
            addendum_id=addendum.uuid,
        )
        assert canceled.status == ContractAddendum.StatusChoices.CANCELED

        ContractAddendumService.delete(
            company=user.company,
            contract_id=contract.uuid,
            addendum_id=addendum.uuid,
        )
        assert not ContractAddendum.objects.filter(pk=addendum.pk).exists()
