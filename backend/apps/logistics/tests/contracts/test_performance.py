from decimal import Decimal

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.finances.tests.factories import ExpenseFactory, InstallmentFactory
from apps.logistics.schemas import ContractOut
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestContractPerformance:
    def test_list_contracts_serialization_queries(self, user):
        wedding = WeddingFactory(user_context=user)

        ContractFactory.create_batch(5, wedding=wedding, company=user.company)

        contracts = list(ContractService.list(user.company, wedding_id=wedding.uuid))

        assert len(contracts) == 5

        with CaptureQueriesContext(connection) as queries:
            for contract in contracts:
                data = ContractOut.from_orm(contract).dict()
                _ = data["supplier_name"]
                _ = data["addendums_count"]

        msg = f"Deveria ter 0 queries na serialização, mas obteve {len(queries)}"
        assert len(queries) == 0, msg

    def test_list_contracts_with_expenses_serialization(self, user):
        wedding = WeddingFactory(user_context=user)

        for _ in range(5):
            contract = ContractFactory(wedding=wedding, company=user.company)
            ExpenseFactory(
                wedding=wedding,
                company=user.company,
                contract=contract,
            )

        contracts = list(ContractService.list(user.company, wedding_id=wedding.uuid))

        assert len(contracts) == 5

        with CaptureQueriesContext(connection) as queries:
            for contract in contracts:
                data = ContractOut.from_orm(contract).dict()
                _ = data["expense_uuid"]
                _ = data["has_linked_expense"]
                _ = data["supplier_name"]

        msg = f"Deveria ter 0 queries na serialização com despesas, mas obteve {len(queries)}"
        assert len(queries) == 0, msg

    def test_single_contract_serialization_efficiency(self, user):
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)

        db_contract = ContractService.get(user.company, contract.uuid)

        with CaptureQueriesContext(connection) as queries:
            data = ContractOut.from_orm(db_contract).dict()
            _ = data["addendums_count"]

        assert len(queries) == 0, f"Deveria ter 0 queries, mas obteve {len(queries)}"

    def test_progress_percent_with_paid_installments(self, user):
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(
            wedding=wedding, company=user.company, total_amount=Decimal("1000.00")
        )
        expense = ExpenseFactory(
            wedding=wedding, company=user.company, contract=contract,
        )
        InstallmentFactory(
            expense=expense, amount=Decimal("300.00"), status="PAID",
        )
        InstallmentFactory(
            expense=expense, amount=Decimal("200.00"), status="PAID",
        )

        db_contract = ContractService.get(user.company, contract.uuid)
        data = ContractOut.from_orm(db_contract).dict()
        assert data["progress_percent"] == 50
