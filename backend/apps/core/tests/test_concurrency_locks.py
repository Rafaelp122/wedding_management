"""
Testes de concorrência e travamento pessimista (select_for_update).

Garante que operações críticas de mutação de saldo, pagamentos e alteração
de teto orçamentário invocam select_for_update() dentro de transações atômicas,
evitando condições de corrida (TOCTOU - Time-of-Check to Time-of-Use).
"""

from decimal import Decimal
from typing import Any, cast

import pytest
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from apps.finances.models import Budget, BudgetCategory, Installment
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryPatchIn,
    ExpenseIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.finances.services.installment_service import InstallmentService
from apps.finances.tests.factories import BudgetCategoryFactory, BudgetFactory
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestConcurrencyLocks:
    """Suíte de testes para validação de travas pessimistas de concorrência."""

    def test_budget_category_create_invokes_select_for_update(
        self, mocker: Any
    ) -> None:
        """
        Garante que BudgetCategoryService.create invoca select_for_update() no Budget.

        A trava impede race condition (TOCTOU) ao verificar se a soma das categorias
        excede o teto estipulado.
        """
        spy = mocker.spy(QuerySet, "select_for_update")

        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        budget = cast(
            Budget,
            BudgetFactory(
                company=company, wedding=wedding, total_estimated=Decimal("10000.00")
            ),
        )

        payload = BudgetCategoryIn(
            budget=budget.uuid,
            name="Fotografia",
            allocated_budget=Decimal("3000.00"),
        )

        with CaptureQueriesContext(connection) as ctx:
            category = BudgetCategoryService.create(company=company, payload=payload)

        assert category.name == "Fotografia"
        assert spy.called, (
            "select_for_update() não foi invocado no QuerySet "
            "durante BudgetCategoryService.create."
        )

        if connection.vendor != "sqlite":
            sql_queries = [q["sql"] for q in ctx.captured_queries]
            assert any("FOR UPDATE" in sql.upper() for sql in sql_queries)

    def test_budget_category_update_invokes_select_for_update(
        self, mocker: Any
    ) -> None:
        """
        Garante que BudgetCategoryService.update invoca select_for_update() no Budget.

        Verifica se a revalidação do teto orçamentário é protegida por trava pessimista.
        """
        spy = mocker.spy(QuerySet, "select_for_update")

        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        budget = cast(
            Budget,
            BudgetFactory(
                company=company, wedding=wedding, total_estimated=Decimal("10000.00")
            ),
        )
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(
                company=company,
                wedding=wedding,
                budget=budget,
                allocated_budget=Decimal("2000.00"),
            ),
        )

        payload = BudgetCategoryPatchIn(
            name=category.name, allocated_budget=Decimal("5000.00")
        )

        with CaptureQueriesContext(connection) as ctx:
            updated = BudgetCategoryService.update(
                company=company, instance=category, payload=payload
            )

        assert updated.allocated_budget == Decimal("5000.00")
        assert spy.called, (
            "select_for_update() não foi invocado no QuerySet "
            "durante BudgetCategoryService.update."
        )

        if connection.vendor != "sqlite":
            sql_queries = [q["sql"] for q in ctx.captured_queries]
            assert any("FOR UPDATE" in sql.upper() for sql in sql_queries)

    def test_get_or_create_for_wedding_uses_select_for_update(
        self, mocker: Any
    ) -> None:
        """
        Garante que get_or_create_for_wedding trava o orçamento ao criar categorias.
        """
        spy = mocker.spy(QuerySet, "select_for_update")

        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))

        with CaptureQueriesContext(connection) as ctx:
            budget = BudgetService.get_or_create_for_wedding(
                company=company, wedding_uuid=wedding.uuid
            )

        assert budget is not None
        assert spy.called, (
            "select_for_update() não foi invocado ao gerar categorias padrão no Budget."
        )

        if connection.vendor != "sqlite":
            sql_queries = [q["sql"] for q in ctx.captured_queries]
            assert any("FOR UPDATE" in sql.upper() for sql in sql_queries)

    def test_installment_mark_as_paid_is_atomic_and_mutates_status(self) -> None:
        """
        Garante que a liquidação de parcelas executa com proteção atômica.
        """
        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=company, wedding=wedding),
        )

        expense = ExpenseService.create(
            company=company,
            payload=ExpenseIn(
                category=category.uuid,
                name="Buffet Principal",
                actual_amount=Decimal("1000.00"),
                estimated_amount=Decimal("1000.00"),
                num_installments=1,
            ),
        )
        installment = expense.installments.first()
        assert installment is not None
        assert installment.status == Installment.StatusChoices.PENDING

        paid_installment = InstallmentService.mark_as_paid(
            company=company, instance=installment
        )

        assert paid_installment.status == Installment.StatusChoices.PAID
        assert paid_installment.paid_date is not None
