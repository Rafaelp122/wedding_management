"""
Testes unitários e de integração para WeddingSummarySelector em apps/reporting.
Valida o isolamento de métricas cruzadas analíticas (finanças, agenda e casamentos).
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.utils import timezone

from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.reporting.selectors.summaries import WeddingSummarySelector
from apps.scheduler.tests.factories import TaskFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestWeddingSummarySelector:
    """Testes para o seletor analítico consolidado de casamentos."""

    def test_list_weddings_with_metrics(self, user: Any) -> None:
        """Anota budget, overdue_installments e incomplete_tasks."""
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(
            wedding=wedding, company=user.company, total_estimated=Decimal("50000.00")
        )
        category = BudgetCategoryFactory(
            budget=budget, wedding=wedding, company=user.company
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, contract=None, company=user.company
        )

        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("1000.00"),
            due_date=today - timedelta(days=5),
            status=Installment.StatusChoices.OVERDUE,
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
        )

        qs = WeddingSummarySelector.list_weddings_with_metrics(company=user.company)
        result = qs.first()

        assert result is not None
        annotated = cast(Any, result)
        assert float(annotated.total_budget) == 50000.0
        assert annotated.overdue_installments == 1
        assert annotated.incomplete_tasks == 1

    def test_list_weddings_with_metrics_without_budget(self, user: Any) -> None:
        """total_budget é None quando não há orçamento associado."""
        WeddingFactory(company=user.company)

        qs = WeddingSummarySelector.list_weddings_with_metrics(company=user.company)
        result = qs.first()

        assert result is not None
        annotated = cast(Any, result)
        assert annotated.total_budget is None
        assert annotated.overdue_installments == 0
        assert annotated.incomplete_tasks == 0

    def test_critical_weddings(self, user: Any) -> None:
        """Anota métricas críticas para casamentos nos próximos 90 dias."""
        today = timezone.localdate()
        wedding = WeddingFactory(
            company=user.company,
            date=today + timedelta(days=10),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        budget = BudgetFactory(wedding=wedding, company=user.company)
        category = BudgetCategoryFactory(
            budget=budget, wedding=wedding, company=user.company
        )
        expense = ExpenseFactory(
            wedding=wedding, category=category, contract=None, company=user.company
        )

        # 1. Parcela pendente futura
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today + timedelta(days=10),
        )
        # 2. Parcela atrasada
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            status=Installment.StatusChoices.OVERDUE,
            due_date=today - timedelta(days=5),
        )
        # 3. Tarefa atrasada (< today)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today - timedelta(days=2),
        )
        # 4. Tarefa pendente futura
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=today + timedelta(days=5),
        )
        # 5. Tarefa concluída (não deve contar)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=today - timedelta(days=3),
        )

        # Casamento cancelado não deve entrar
        WeddingFactory(
            company=user.company,
            date=today + timedelta(days=15),
            status=Wedding.StatusChoices.CANCELED,
        )

        qs = WeddingSummarySelector.critical_weddings(
            company=user.company, today=today, limit=5
        )
        result = qs.first()

        assert result is not None
        assert result.uuid == wedding.uuid
        annotated = cast(Any, result)
        assert annotated.incomplete_tasks == 2
        assert annotated.pending_installments == 1
        assert annotated.overdue_tasks == 1
        assert annotated.overdue_installments == 1
