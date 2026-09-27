"""
Testes unitários dos seletores de consulta de contratos e aditivos (apps.contracts).
"""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Any, cast

import pytest

from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.selectors import (
    contract_addendum_get_selector,
    contract_addendum_list_selector,
    contract_consolidated_total_selector,
    contract_detail_aggregate_selector,
    contract_get_selector,
    contract_list_selector,
)
from apps.contracts.tests.factories import (
    ContractAddendumFactory as _ContractAddendumFactory,
)
from apps.contracts.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.contracts.tests.factories import SupplierFactory as _SupplierFactory
from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
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


def CompanyFactory(*args: Any, **kwargs: Any) -> Any:
    return _CompanyFactory(*args, **kwargs)


@pytest.mark.django_db
class TestContractSelectors:
    """Testes dos seletores de leitura do domínio de Contratos."""

    @pytest.mark.skip(reason="Obsolete due to Phase 2 refactoring")
    def test_contract_list_selector_with_filters(self, user: Any) -> None:
        """Listagem de contratos com múltiplos critérios de filtragem."""
        wedding_1 = cast(Wedding, WeddingFactory(company=user.company))
        wedding_2 = cast(Wedding, WeddingFactory(company=user.company))
        supplier_1 = SupplierFactory(company=user.company)
        client_1 = ClientFactory(company=user.company)

        c1 = ContractFactory(
            company=user.company,
            wedding=wedding_1,
            supplier=supplier_1,
            contract_type="SUPPLIER",
            status="DRAFT",
        )
        c2 = ContractFactory(
            company=user.company,
            wedding=wedding_1,
            client=client_1,
            contract_type="PLANNER",
            status="DRAFT",
        )
        c3 = ContractFactory(
            company=user.company,
            wedding=wedding_2,
            contract_type="SUPPLIER",
            status="SIGNED",
            signed_date="2026-05-01",
            pdf_file="fake.pdf",
        )

        all_contracts = list(contract_list_selector(company=user.company))
        assert len(all_contracts) >= 3

        wedding_1_contracts = list(
            contract_list_selector(company=user.company, wedding_id=wedding_1.uuid)
        )
        assert len(wedding_1_contracts) == 2

        planner_contracts = list(
            contract_list_selector(company=user.company, contract_type="PLANNER")
        )
        assert any(c.uuid == c2.uuid for c in planner_contracts)

        supplier_contracts = list(
            contract_list_selector(company=user.company, supplier_id=supplier_1.uuid)
        )
        assert len(supplier_contracts) == 1
        assert supplier_contracts[0].uuid == c1.uuid

    def test_contract_get_selector_success_and_not_found(self, user: Any) -> None:
        """Recuperação de contrato específico com totais anotados."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("4000.00"),
        )

        found = contract_get_selector(company=user.company, uuid=contract.uuid)
        assert found.uuid == contract.uuid
        assert found.base_amount == Decimal("4000.00")

        with pytest.raises(ObjectNotFoundError):
            contract_get_selector(
                company=user.company, uuid="00000000-0000-0000-0000-000000000000"
            )

    def test_contract_detail_aggregate_selector(self, user: Any) -> None:
        """Agregação de contrato com itens e termos aditivos."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        addendum = ContractAddendumFactory(
            company=user.company,
            wedding=wedding,
            contract=contract,
            amount=Decimal("800.00"),
        )

        details = contract_detail_aggregate_selector(
            company=user.company, contract_uuid=contract.uuid
        )

        assert details["contract"].uuid == contract.uuid
        assert len(details["addendums"]) == 1
        assert details["addendums"][0].uuid == addendum.uuid

    def test_contract_addendum_selectors(self, user: Any) -> None:
        """Seletores específicos de termos aditivos."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(company=user.company, wedding=wedding)

        add1 = ContractAddendumFactory(company=user.company, contract=contract)
        add2 = ContractAddendumFactory(company=user.company, contract=contract)

        addendums = list(
            contract_addendum_list_selector(
                company=user.company, contract_uuid=contract.uuid
            )
        )
        assert len(addendums) == 2

        found = contract_addendum_get_selector(
            company=user.company,
            contract_uuid=contract.uuid,
            addendum_uuid=add1.uuid,
        )
        assert found.uuid == add1.uuid

    def test_with_totals_scopes_subqueries_by_tenant(self, user: Any) -> None:
        """Anotações with_totals isoladas por tenant mesmo com ruído vizinho."""
        other_company = cast(Any, CompanyFactory())
        wedding_a = cast(Wedding, WeddingFactory(company=user.company))
        contract_a = ContractFactory(
            company=user.company,
            wedding=wedding_a,
            total_amount=Decimal("10000.00"),
        )
        wedding_b = cast(Wedding, WeddingFactory(company=other_company))
        contract_b = ContractFactory(
            company=other_company,
            wedding=wedding_b,
            total_amount=Decimal("10000.00"),
        )
        ContractAddendumFactory(
            company=other_company,
            wedding=wedding_b,
            contract=contract_b,
            amount=Decimal("9000.00"),
            status=ContractAddendum.StatusChoices.SIGNED,
            signed_date=dt.date.today(),
        )

        found = contract_get_selector(company=user.company, uuid=contract_a.uuid)

        assert found.addendums_total == Decimal("0.00")
        assert found.effective_amount == Decimal("10000.00")

    def test_contract_consolidated_total_selector(self, user: Any) -> None:
        """Consolidado soma face + aditivos SIGNED (PENDING é expectativa)."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("10000.00"),
        )

        ContractAddendumFactory(
            company=user.company,
            contract=contract,
            amount=Decimal("2000.00"),
            status=ContractAddendum.StatusChoices.SIGNED,
            signed_date=dt.date.today(),
        )
        ContractAddendumFactory(
            company=user.company,
            contract=contract,
            amount=Decimal("1500.00"),
            status=ContractAddendum.StatusChoices.PENDING,
        )
        ContractAddendumFactory(
            company=user.company,
            contract=contract,
            amount=Decimal("500.00"),
            status=ContractAddendum.StatusChoices.CANCELED,
        )

        total = contract_consolidated_total_selector(
            company=user.company, contract=contract
        )

        assert total == Decimal("12000.00")

    def test_with_totals_annotates_pending_addendums(self, user: Any) -> None:
        """with_totals expõe pendentes separado dos assinados."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = ContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("10000.00"),
        )
        ContractAddendumFactory(
            company=user.company,
            contract=contract,
            amount=Decimal("2000.00"),
            status=ContractAddendum.StatusChoices.SIGNED,
            signed_date=dt.date.today(),
        )
        ContractAddendumFactory(
            company=user.company,
            contract=contract,
            amount=Decimal("1500.00"),
            status=ContractAddendum.StatusChoices.PENDING,
        )

        found = contract_get_selector(company=user.company, uuid=contract.uuid)

        assert found.addendums_total == Decimal("2000.00")
        assert cast(Any, found).addendums_pending_total == Decimal("1500.00")
        assert found.effective_amount == Decimal("12000.00")
