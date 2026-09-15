"""
Testes unitários para as interfaces públicas do app scheduler
(apps/scheduler/interfaces.py).
"""

from datetime import date, timedelta
from decimal import Decimal
from typing import Any, cast

import pytest
from django.utils import timezone

from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.scheduler.interfaces import (
    apply_wedding_schedule_template,
    create_payment_events_for_installments,
    delete_payment_event_for_installment,
    delete_payment_events_for_expense,
)
from apps.scheduler.models import Event
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestSchedulerInterfaces:
    """Valida as operações expostas na fachada do scheduler."""

    def test_create_and_delete_payment_events_for_installments(self, user: Any) -> None:
        today = date.today()
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding, company=user.company)
        category = BudgetCategoryFactory(
            budget=budget, wedding=wedding, company=user.company
        )
        expense = cast(
            Any,
            ExpenseFactory(
                wedding=wedding, category=category, contract=None, company=user.company
            ),
        )

        i1 = cast(
            Any,
            InstallmentFactory(
                expense=expense,
                wedding=wedding,
                company=user.company,
                amount=Decimal("500.00"),
                due_date=today + timedelta(days=10),
                installment_number=1,
            ),
        )
        i2 = cast(
            Any,
            InstallmentFactory(
                expense=expense,
                wedding=wedding,
                company=user.company,
                amount=Decimal("500.00"),
                due_date=today + timedelta(days=40),
                installment_number=2,
            ),
        )

        create_payment_events_for_installments(
            company=user.company, expense=expense, installments=[i1, i2]
        )

        events = Event.objects.for_tenant(user.company).filter(
            event_type="pagamento", wedding=wedding
        )
        assert events.count() == 2

        # Deleta apenas da parcela 1
        delete_payment_event_for_installment(company=user.company, installment=i1)
        assert events.count() == 1
        first_event = events.first()
        assert first_event is not None
        assert first_event.source_installment_id == i2.id

        # Deleta todos da despesa
        delete_payment_events_for_expense(company=user.company, expense=expense)
        assert events.count() == 0

    def test_apply_wedding_schedule_template(self, user: Any) -> None:
        today = timezone.localdate()
        wedding = WeddingFactory(
            company=user.company,
            date=today + timedelta(days=200),
        )

        apply_wedding_schedule_template(
            company=user.company,
            wedding=wedding,
            template_name="religious_12m",
        )

        events = Event.objects.for_tenant(user.company).filter(wedding=wedding)
        assert events.count() > 0
