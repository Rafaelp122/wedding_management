"""
Testes de desempenho de API e prevenção de N+1 queries SQL.

Valida que os endpoints de listagem do sistema possuem complexidade de consulta
constante O(1), independente da quantidade de itens persistidos na base.
"""

from collections.abc import Callable
from typing import Any

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.finances.tests.factories import BudgetCategoryFactory, ExpenseFactory
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.scheduler.tests.factories import EventFactory
from apps.weddings.tests.factories import WeddingFactory


def _setup_expenses(company: Any) -> Callable[[int], None]:
    wedding = WeddingFactory(company=company)
    category = BudgetCategoryFactory(company=company, wedding=wedding)

    def _create(count: int) -> None:
        ExpenseFactory.create_batch(
            count, company=company, wedding=wedding, category=category
        )

    return _create


def _setup_suppliers(company: Any) -> Callable[[int], None]:
    def _create(count: int) -> None:
        SupplierFactory.create_batch(count, company=company)

    return _create


def _setup_contracts(company: Any) -> Callable[[int], None]:
    wedding = WeddingFactory(company=company)
    supplier = SupplierFactory(company=company)

    def _create(count: int) -> None:
        ContractFactory.create_batch(
            count, company=company, wedding=wedding, supplier=supplier
        )

    return _create


def _setup_events(company: Any) -> Callable[[int], None]:
    wedding = WeddingFactory(company=company)

    def _create(count: int) -> None:
        EventFactory.create_batch(count, company=company, wedding=wedding)

    return _create


def _setup_weddings(company: Any) -> Callable[[int], None]:
    def _create(count: int) -> None:
        WeddingFactory.create_batch(count, company=company)

    return _create


@pytest.mark.django_db
class TestApiPerformanceNPlusOne:
    """Suíte de testes parametrizada de queries SQL para prevenção de N+1."""

    @pytest.mark.parametrize(
        "endpoint, setup_func",
        [
            ("/api/v1/finances/expenses/", _setup_expenses),
            ("/api/v1/logistics/suppliers/", _setup_suppliers),
            ("/api/v1/logistics/contracts/", _setup_contracts),
            ("/api/v1/scheduler/events/", _setup_events),
            ("/api/v1/weddings/", _setup_weddings),
        ],
    )
    def test_list_endpoint_query_count_is_constant(
        self, auth_client: Any, endpoint: str, setup_func: Callable[[Any], Any]
    ) -> None:
        """
        Valida que o endpoint de listagem executa O(1) queries.

        Compara o número de queries executadas ao listar 1 item versus 10 itens.
        """
        company = auth_client.user.company
        create_batch = setup_func(company)

        # 1 item
        create_batch(1)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get(endpoint)
        assert resp_1.status_code == 200

        # 9 mais itens (total 10)
        create_batch(9)
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get(endpoint)
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em {endpoint}: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )
