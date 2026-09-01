"""
Testes unitários e de integração para Selectors e QuerySets do domínio de Weddings.
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.scheduler.tests.factories import TaskFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.managers import WeddingQuerySet
from apps.weddings.models import Wedding
from apps.weddings.selectors import (
    critical_weddings_selector,
    wedding_count_by_month_selector,
    wedding_get_selector,
    wedding_list_selector,
    wedding_lookup_selector,
)
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestWeddingQuerySet:
    """Testes para os métodos encadeáveis do WeddingQuerySet."""

    def test_with_metrics(self, user: Any) -> None:
        """with_metrics() anota budget, overdue_installments e incomplete_tasks."""
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

        qs = Wedding.objects.for_tenant(user.company).with_metrics()
        result = qs.first()

        assert result is not None
        assert isinstance(qs, WeddingQuerySet)
        annotated = cast(Any, result)
        assert float(annotated.total_budget) == 50000.0
        assert annotated.overdue_installments == 1
        assert annotated.incomplete_tasks == 1

    def test_with_metrics_without_budget(self, user: Any) -> None:
        """total_budget é None quando não há orçamento associado."""
        WeddingFactory(company=user.company)

        qs = Wedding.objects.for_tenant(user.company).with_metrics()
        result = qs.first()

        assert result is not None
        annotated = cast(Any, result)
        assert annotated.total_budget is None
        assert annotated.overdue_installments == 0
        assert annotated.incomplete_tasks == 0

    def test_with_critical_metrics(self, user: Any) -> None:
        """with_critical_metrics() anota métricas para o dashboard crítico."""
        today = date(2026, 8, 16)
        wedding = WeddingFactory(company=user.company)
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
        # 5. Tarefa concluída (não deve contar em incompletas nem em atrasadas)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=today - timedelta(days=3),
        )

        qs = Wedding.objects.for_tenant(user.company).with_critical_metrics(today=today)
        result = qs.first()

        assert result is not None
        annotated = cast(Any, result)
        assert annotated.incomplete_tasks == 2
        assert annotated.pending_installments == 1
        assert annotated.overdue_tasks == 1
        assert annotated.overdue_installments == 1

    def test_search_by_groom_bride_location(self, user: Any) -> None:
        """search() filtra case-insensitive por noivo, noiva e local."""
        w1 = WeddingFactory(
            company=user.company,
            groom_name="Rodrigo Silva",
            bride_name="Fernanda Lima",
            location="Praia de Camburi",
        )
        w2 = WeddingFactory(
            company=user.company,
            groom_name="Carlos Eduardo",
            bride_name="Juliana Paes",
            location="Igreja Matriz",
        )

        qs_groom = Wedding.objects.for_tenant(user.company).search("rodrigo")
        assert list(qs_groom) == [w1]

        qs_bride = Wedding.objects.for_tenant(user.company).search("juliana")
        assert list(qs_bride) == [w2]

        qs_location = Wedding.objects.for_tenant(user.company).search("camburi")
        assert list(qs_location) == [w1]

        qs_empty = Wedding.objects.for_tenant(user.company).search("")
        assert qs_empty.count() == 2

    def test_by_status(self, user: Any) -> None:
        """by_status() filtra por status válido e levanta exceção para inválido."""
        w_in_progress = WeddingFactory(
            company=user.company, status=Wedding.StatusChoices.IN_PROGRESS
        )
        w_canceled = WeddingFactory(
            company=user.company, status=Wedding.StatusChoices.CANCELED
        )

        qs_prog = Wedding.objects.for_tenant(user.company).by_status("IN_PROGRESS")
        assert list(qs_prog) == [w_in_progress]

        qs_canc = Wedding.objects.for_tenant(user.company).by_status("CANCELED")
        assert list(qs_canc) == [w_canceled]

        qs_all = Wedding.objects.for_tenant(user.company).by_status("")
        assert qs_all.count() == 2

        with pytest.raises(BusinessRuleViolation) as exc_info:
            Wedding.objects.for_tenant(user.company).by_status("INVALID_STATUS")

        assert exc_info.value.code == "wedding_invalid_status_filter"

    def test_upcoming(self, user: Any) -> None:
        """upcoming() filtra casamentos até today + days."""
        today = date(2026, 8, 16)
        w_near = WeddingFactory(company=user.company, date=today + timedelta(days=30))
        WeddingFactory(company=user.company, date=today + timedelta(days=120))

        qs = Wedding.objects.for_tenant(user.company).upcoming(today=today, days=90)
        assert list(qs) == [w_near]

    def test_only_lookup(self, user: Any) -> None:
        """only_lookup() restringe campos e ordena por bride_name."""
        WeddingFactory(company=user.company, bride_name="Zélia", groom_name="Beto")
        WeddingFactory(company=user.company, bride_name="Alice", groom_name="Carlos")

        qs = Wedding.objects.for_tenant(user.company).only_lookup()
        results = list(qs)

        assert len(results) == 2
        assert results[0].bride_name == "Alice"
        assert results[1].bride_name == "Zélia"

    def test_chainable_methods(self, user: Any) -> None:
        """Garante encadeamento fluente de múltiplos métodos no QuerySet."""
        today = date(2026, 8, 16)
        w = WeddingFactory(
            company=user.company,
            bride_name="Mariana",
            groom_name="Lucas",
            status=Wedding.StatusChoices.IN_PROGRESS,
            date=today + timedelta(days=20),
        )

        qs = (
            Wedding.objects.for_tenant(user.company)
            .search("Mariana")
            .by_status("IN_PROGRESS")
            .upcoming(today=today, days=60)
            .with_metrics()
        )

        assert list(qs) == [w]
        assert hasattr(qs.first(), "incomplete_tasks")


@pytest.mark.django_db
class TestWeddingSelectors:
    """Testes para as funções seletoras de casamento."""

    def test_wedding_list_selector_multitenancy_and_filters(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()

        w_a1 = WeddingFactory(
            company=user_a.company,
            bride_name="Ana",
            groom_name="Bruno",
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        WeddingFactory(
            company=user_a.company,
            bride_name="Carla",
            groom_name="Daniel",
            status=Wedding.StatusChoices.CANCELED,
        )
        WeddingFactory(
            company=user_b.company,
            bride_name="Ana",
            groom_name="Eduardo",
        )

        qs_a = wedding_list_selector(
            company=user_a.company, search="Ana", status="IN_PROGRESS"
        )
        assert list(qs_a) == [w_a1]

    def test_wedding_get_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company, bride_name="Noiva Selector")

        result = wedding_get_selector(company=user.company, uuid=wedding.uuid)

        assert result.uuid == wedding.uuid
        assert result.bride_name == "Noiva Selector"

    def test_wedding_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError) as exc_info:
            wedding_get_selector(company=user.company, uuid=uuid4())

        assert exc_info.value.code == "wedding_not_found_or_denied"

    def test_wedding_get_selector_cross_tenant(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            wedding_get_selector(company=user_a.company, uuid=wedding_b.uuid)

    def test_wedding_lookup_selector(self, user: Any) -> None:
        WeddingFactory(company=user.company, bride_name="Zilda")
        WeddingFactory(company=user.company, bride_name="Beatriz")

        qs = wedding_lookup_selector(company=user.company)
        items = list(qs)

        assert len(items) == 2
        assert items[0].bride_name == "Beatriz"
        assert items[1].bride_name == "Zilda"

    def test_wedding_count_by_month_selector(self, user: Any) -> None:
        future_year = date.today().year + 1
        WeddingFactory(company=user.company, date=date(future_year, 3, 10))
        WeddingFactory(company=user.company, date=date(future_year, 3, 20))
        WeddingFactory(company=user.company, date=date(future_year, 7, 15))

        counts = wedding_count_by_month_selector(company=user.company, year=future_year)

        assert counts == [
            {"month": 3, "count": 2},
            {"month": 7, "count": 1},
        ]

    def test_wedding_count_by_month_selector_empty(self, user: Any) -> None:
        counts = wedding_count_by_month_selector(company=user.company, year=1999)
        assert counts == []

    def test_critical_weddings_selector(self, user: Any) -> None:
        today = timezone.localdate()
        w1 = WeddingFactory(
            company=user.company,
            date=today + timedelta(days=10),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        w2 = WeddingFactory(
            company=user.company,
            date=today + timedelta(days=20),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        # Mais de 90 dias não deve entrar
        WeddingFactory(
            company=user.company,
            date=today + timedelta(days=100),
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        # Cancelado não deve entrar
        WeddingFactory(
            company=user.company,
            date=today + timedelta(days=15),
            status=Wedding.StatusChoices.CANCELED,
        )

        qs = critical_weddings_selector(company=user.company, today=today, limit=5)
        assert list(qs) == [w1, w2]
        assert hasattr(qs[0], "incomplete_tasks")
        assert hasattr(qs[0], "overdue_installments")
