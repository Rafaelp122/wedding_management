"""
Testes de desempenho de API e prevenção de N+1 queries SQL.

Valida que os endpoints de listagem do sistema possuem complexidade de consulta
constante O(1), independente da quantidade de itens persistidos na base.
"""

from typing import Any

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.finances.tests.factories import BudgetCategoryFactory, ExpenseFactory
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.scheduler.tests.factories import EventFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestApiPerformanceNPlusOne:
    """Suíte de testes de contagem de queries SQL para prevenção de N+1."""

    def test_expenses_list_query_count_is_constant(self, auth_client: Any) -> None:
        """
        Valida que GET /api/v1/finances/expenses/ executa O(1) queries.

        Compara o número de queries executadas ao listar 1 despesa versus 10 despesas.
        """
        company = auth_client.user.company
        wedding = WeddingFactory(company=company)
        category = BudgetCategoryFactory(company=company, wedding=wedding)

        ExpenseFactory(company=company, wedding=wedding, category=category)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get("/api/v1/finances/expenses/")
        assert resp_1.status_code == 200

        ExpenseFactory.create_batch(
            9, company=company, wedding=wedding, category=category
        )
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get("/api/v1/finances/expenses/")
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em /finances/expenses/: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )

    def test_suppliers_list_query_count_is_constant(self, auth_client: Any) -> None:
        """
        Valida que GET /api/v1/logistics/suppliers/ executa O(1) queries.

        Compara a quantidade de consultas SQL para 1 fornecedor versus 10 fornecedores.
        """
        company = auth_client.user.company

        SupplierFactory(company=company)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get("/api/v1/logistics/suppliers/")
        assert resp_1.status_code == 200

        SupplierFactory.create_batch(9, company=company)
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get("/api/v1/logistics/suppliers/")
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em /logistics/suppliers/: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )

    def test_contracts_list_query_count_is_constant(self, auth_client: Any) -> None:
        """
        Valida que GET /api/v1/logistics/contracts/ executa O(1) queries.

        Compara a quantidade de consultas SQL para 1 contrato versus 10 contratos.
        """
        company = auth_client.user.company
        wedding = WeddingFactory(company=company)
        supplier = SupplierFactory(company=company)

        ContractFactory(company=company, wedding=wedding, supplier=supplier)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get("/api/v1/logistics/contracts/")
        assert resp_1.status_code == 200

        ContractFactory.create_batch(
            9, company=company, wedding=wedding, supplier=supplier
        )
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get("/api/v1/logistics/contracts/")
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em /logistics/contracts/: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )

    def test_events_list_query_count_is_constant(self, auth_client: Any) -> None:
        """
        Valida que GET /api/v1/scheduler/events/ executa O(1) queries.

        Compara o número de queries SQL para 1 evento versus 10 eventos.
        """
        company = auth_client.user.company
        wedding = WeddingFactory(company=company)

        EventFactory(company=company, wedding=wedding)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get("/api/v1/scheduler/events/")
        assert resp_1.status_code == 200

        EventFactory.create_batch(9, company=company, wedding=wedding)
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get("/api/v1/scheduler/events/")
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em /scheduler/events/: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )

    def test_weddings_list_query_count_is_constant(self, auth_client: Any) -> None:
        """
        Valida que GET /api/v1/weddings/ executa O(1) queries.

        Compara o número de queries SQL para 1 casamento versus 10 casamentos.
        """
        company = auth_client.user.company

        WeddingFactory(company=company)
        with CaptureQueriesContext(connection) as ctx_1:
            resp_1 = auth_client.get("/api/v1/weddings/")
        assert resp_1.status_code == 200

        WeddingFactory.create_batch(9, company=company)
        with CaptureQueriesContext(connection) as ctx_10:
            resp_10 = auth_client.get("/api/v1/weddings/")
        assert resp_10.status_code == 200

        queries_1 = len(ctx_1)
        queries_10 = len(ctx_10)

        assert queries_10 == queries_1, (
            f"Regressão N+1 em /weddings/: "
            f"1 item -> {queries_1} queries, 10 itens -> {queries_10} queries."
        )
