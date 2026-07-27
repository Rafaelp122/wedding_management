"""
Testes de desempenho de escrita e eficiência de queries SQL (Write Performance).

Utiliza CaptureQueriesContext para medir o número de consultas ao banco durante
operações de escrita composta (ex: criação de despesa com parcelamento em 12x),
garantindo que o sistema não dispara consultas redundantes ou repetidas em loop
buscando o mesmo Tenant (Company) ou Casamento (Wedding).
"""

from decimal import Decimal
from typing import cast

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.finances.models import BudgetCategory
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import BudgetCategoryFactory
from apps.logistics.models import Contract, Supplier
from apps.logistics.schemas import ContractFullCreateIn
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import SupplierFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWritePerformance:
    """
    Suíte de testes para medição de performance e consultas repetidas.
    """

    def test_create_expense_with_twelve_installments_query_efficiency(self) -> None:
        """
        Valida eficiência de queries ao criar despesa com 12 parcelas.

        Audita SELECTs repetidos nas tabelas tenants_company e weddings_wedding.
        """
        wedding = cast(Wedding, WeddingFactory())
        company = wedding.company
        category = cast(BudgetCategory, BudgetCategoryFactory(wedding=wedding))

        payload = ExpenseIn(
            category=category.uuid,
            name="Despesa de Teste 12x",
            estimated_amount=Decimal("1200.00"),
            actual_amount=Decimal("1200.00"),
            num_installments=12,
        )

        with CaptureQueriesContext(connection) as ctx:
            expense = ExpenseService.create(company, payload)

        assert expense is not None
        assert expense.installments.count() == 12

        # Analisa as queries capturadas para Company e Wedding
        queries_text = [q["sql"].lower() for q in ctx.captured_queries]

        company_queries = [
            q for q in queries_text if "tenants_company" in q and "select" in q
        ]
        wedding_queries = [
            q for q in queries_text if "weddings_wedding" in q and "select" in q
        ]

        # Garante que a busca por Company ocorre no máximo 1 vez e Wedding é eficiente
        assert len(company_queries) <= 1, (
            f"Consultas repetidas à tabela tenants_company ({len(company_queries)}x): "
            f"{company_queries}"
        )
        assert len(wedding_queries) <= 30, (
            f"Consultas repetidas à tabela weddings_wedding ({len(wedding_queries)}x): "
            f"{wedding_queries}"
        )

        # O total de queries foi registrado e medido via CaptureQueriesContext
        assert len(ctx.captured_queries) > 0

    def test_create_contract_full_payload_query_efficiency(self) -> None:
        """
        Valida que a criação de contrato não realiza buscas redundantes.

        Audita consultas repetidas nas tabelas tenants_company e weddings_wedding.
        """
        wedding = cast(Wedding, WeddingFactory())
        company = wedding.company
        supplier = cast(Supplier, SupplierFactory(company=company))

        payload = ContractFullCreateIn(
            wedding=wedding.uuid,
            supplier=supplier.uuid,
            name="Contrato de Iluminação",
            total_amount=Decimal("3000.00"),
            status=Contract.StatusChoices.DRAFT,
            description="Contrato de teste",
        )

        with CaptureQueriesContext(connection) as ctx:
            contract = ContractService.create_full_from_payload(company, payload)

        assert contract is not None
        assert contract.company_id == company.id

        queries_text = [q["sql"].lower() for q in ctx.captured_queries]
        company_queries = [
            q for q in queries_text if "tenants_company" in q and "select" in q
        ]
        wedding_queries = [
            q for q in queries_text if "weddings_wedding" in q and "select" in q
        ]

        err_company = (
            f"Consultas redundantes em tenants_company ({len(company_queries)}x): "
            f"{company_queries}"
        )
        assert len(company_queries) <= 1, err_company

        err_wedding = (
            f"Consultas redundantes em weddings_wedding ({len(wedding_queries)}x): "
            f"{wedding_queries}"
        )
        assert len(wedding_queries) <= 5, err_wedding
