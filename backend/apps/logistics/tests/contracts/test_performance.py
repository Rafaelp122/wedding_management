import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.finances.tests.factories import ExpenseFactory, InstallmentFactory
from apps.logistics.schemas import ContractOut
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.tests.factories import WeddingFactory


def _serialize(contract):
    data = ContractOut.from_orm(contract).dict()
    _ = data["supplier_name"]
    _ = data["addendums_count"]
    _ = data["expense_uuid"]
    _ = data["has_linked_expense"]
    _ = data["progress_percent"]
    return data


@pytest.mark.django_db
class TestContractPerformance:
    def test_list_contracts_serialization_queries(self, user):
        wedding = WeddingFactory(user_context=user)
        ContractFactory.create_batch(5, wedding=wedding, company=user.company)

        contracts = list(ContractService.list(user.company, wedding_id=wedding.uuid))
        assert len(contracts) == 5

        with CaptureQueriesContext(connection) as queries:
            for contract in contracts:
                _serialize(contract)

        assert len(queries) == 0, (
            f"Deveria ter 0 queries na serialização, mas obteve {len(queries)}"
        )

    def test_single_contract_serialization_efficiency(self, user):
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)

        db_contract = ContractService.get(user.company, contract.uuid)

        with CaptureQueriesContext(connection) as queries:
            _serialize(db_contract)

        assert len(queries) == 0, (
            f"Deveria ter 0 queries, mas obteve {len(queries)}"
        )

    def test_list_contracts_with_expenses_serialization(self, user):
        wedding = WeddingFactory(user_context=user)
        contracts = ContractFactory.create_batch(
            5, wedding=wedding, company=user.company
        )

        for contract in contracts:
            expense = ExpenseFactory(
                wedding=wedding, company=user.company, contract=contract
            )
            contract.expense_id = expense.uuid

        contracts = list(ContractService.list(user.company, wedding_id=wedding.uuid))
        assert len(contracts) == 5

        with CaptureQueriesContext(connection) as queries:
            for contract in contracts:
                _serialize(contract)

        assert len(queries) == 0, (
            f"Deveria ter 0 queries na serialização, mas obteve {len(queries)}"
        )

    def test_progress_percent_with_paid_installments(self, user):
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(
            wedding=wedding, company=user.company, total_amount=1000
        )
        expense = ExpenseFactory(
            wedding=wedding, company=user.company, contract=contract,
            actual_amount=1000,
        )
        contract.expense_id = expense.uuid

        InstallmentFactory(
            expense=expense,
            amount=300,
            status="PAID",
            wedding=wedding,
            company=user.company,
        )

        db_contract = ContractService.get(user.company, contract.uuid)

        data = ContractOut.from_orm(db_contract).dict()
        assert data["progress_percent"] == 30
