"""
Testes unitários e de integração para Selectors e QuerySets do Scheduler.
"""

from datetime import date, timedelta
from typing import Any, cast
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.core.exceptions import ObjectNotFoundError
from apps.scheduler.managers import TaskQuerySet
from apps.scheduler.models import Event, Task
from apps.scheduler.selectors import (
    event_get_selector,
    event_list_selector,
    task_get_selector,
    task_list_selector,
    task_urgent_list_selector,
)
from apps.scheduler.tests.factories import EventFactory as _EventFactory
from apps.scheduler.tests.factories import TaskFactory as _TaskFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def EventFactory(*args: Any, **kwargs: Any) -> Event:
    return cast(Event, _EventFactory(*args, **kwargs))


def TaskFactory(*args: Any, **kwargs: Any) -> Task:
    return cast(Task, _TaskFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestTaskQuerySet:
    """Testes dos métodos encadeáveis do TaskQuerySet."""

    def test_for_wedding_with_instance(self, user: Any) -> None:
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        t1 = TaskFactory(wedding=wedding1, title="Tarefa W1")
        TaskFactory(wedding=wedding2, title="Tarefa W2")

        qs = Task.objects.for_tenant(user.company).for_wedding(wedding1)
        assert isinstance(qs, TaskQuerySet)
        assert list(qs) == [t1]

    def test_for_wedding_with_uuid_and_str_and_int(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        t = TaskFactory(wedding=wedding)

        qs_uuid = Task.objects.for_tenant(user.company).for_wedding(wedding.uuid)
        assert list(qs_uuid) == [t]

        qs_str = Task.objects.for_tenant(user.company).for_wedding(str(wedding.uuid))
        assert list(qs_str) == [t]

        qs_int = Task.objects.for_tenant(user.company).for_wedding(wedding.id)
        assert list(qs_int) == [t]

    def test_completed_and_pending(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        t_done = TaskFactory(wedding=wedding, is_completed=True, title="Feita")
        t_pending = TaskFactory(wedding=wedding, is_completed=False, title="Pendente")

        completed_qs = Task.objects.for_tenant(user.company).completed()
        pending_qs = Task.objects.for_tenant(user.company).pending()

        assert list(completed_qs) == [t_done]
        assert list(pending_qs) == [t_pending]

    def test_urgent(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        today = date(2026, 8, 16)

        t_overdue = TaskFactory(
            wedding=wedding,
            due_date=today - timedelta(days=2),
            is_completed=False,
            title="Atrasada",
        )
        t_today = TaskFactory(
            wedding=wedding,
            due_date=today,
            is_completed=False,
            title="Hoje",
        )
        # Concluída não deve entrar
        TaskFactory(
            wedding=wedding,
            due_date=today - timedelta(days=1),
            is_completed=True,
            title="Atrasada Concluída",
        )
        # Futura não deve entrar
        TaskFactory(
            wedding=wedding,
            due_date=today + timedelta(days=1),
            is_completed=False,
            title="Futura",
        )

        urgent_qs = Task.objects.for_tenant(user.company).urgent(today)
        assert set(urgent_qs) == {t_overdue, t_today}

    def test_due_in_range(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        d1 = date(2026, 8, 10)
        d2 = date(2026, 8, 20)

        TaskFactory(wedding=wedding, due_date=date(2026, 8, 5))
        t_mid = TaskFactory(wedding=wedding, due_date=date(2026, 8, 15))
        TaskFactory(wedding=wedding, due_date=date(2026, 8, 25))

        qs = Task.objects.for_tenant(user.company).due_in_range(d1, d2)
        assert list(qs) == [t_mid]


@pytest.mark.django_db
class TestEventQuerySet:
    """Testes dos métodos encadeáveis do EventQuerySet."""

    def test_for_wedding_with_various_types(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        e = EventFactory(wedding=wedding)

        qs = Event.objects.for_tenant(user.company)
        assert list(qs.for_wedding(wedding)) == [e]
        assert list(qs.for_wedding(wedding.uuid)) == [e]
        assert list(qs.for_wedding(str(wedding.uuid))) == [e]
        assert list(qs.for_wedding(wedding.id)) == [e]

    def test_chronological(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        e3 = EventFactory(wedding=wedding, start_time=now + timedelta(days=3))
        e1 = EventFactory(wedding=wedding, start_time=now + timedelta(days=1))
        e2 = EventFactory(wedding=wedding, start_time=now + timedelta(days=2))

        qs = Event.objects.for_tenant(user.company).chronological()
        assert list(qs) == [e1, e2, e3]

    def test_in_period(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()

        EventFactory(wedding=wedding, start_time=now - timedelta(days=5))
        e_in = EventFactory(wedding=wedding, start_time=now + timedelta(days=2))
        EventFactory(wedding=wedding, start_time=now + timedelta(days=10))

        start_dt = now
        end_dt = now + timedelta(days=5)

        qs = Event.objects.for_tenant(user.company).in_period(start_dt, end_dt)
        assert list(qs) == [e_in]

    def test_by_type(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        e_meeting = EventFactory(wedding=wedding, event_type=Event.TypeChoices.MEETING)
        EventFactory(wedding=wedding, event_type=Event.TypeChoices.TASTING)

        qs = Event.objects.for_tenant(user.company).by_type(Event.TypeChoices.MEETING)
        assert list(qs) == [e_meeting]


@pytest.mark.django_db
class TestTaskSelectors:
    """Testes para task selectors."""

    def test_task_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        TaskFactory(wedding=wedding_a, title="Tarefa A")
        TaskFactory(wedding=wedding_b, title="Tarefa B")

        qs_a = task_list_selector(company=user_a.company)
        assert qs_a.count() == 1
        t_a = qs_a.first()
        assert t_a is not None and t_a.title == "Tarefa A"

        qs_b = task_list_selector(company=user_b.company)
        assert qs_b.count() == 1
        t_b = qs_b.first()
        assert t_b is not None and t_b.title == "Tarefa B"

    def test_task_list_selector_filters(self, user: Any) -> None:
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)

        t1 = TaskFactory(wedding=wedding1, is_completed=True, title="T1")
        TaskFactory(wedding=wedding1, is_completed=False, title="T2")
        TaskFactory(wedding=wedding2, is_completed=True, title="T3")

        qs = task_list_selector(
            company=user.company, wedding_id=wedding1.uuid, is_completed=True
        )
        assert list(qs) == [t1]

    def test_task_get_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, title="Revisar Contratos")

        result = task_get_selector(company=user.company, uuid=task.uuid)
        assert result.uuid == task.uuid
        assert result.title == "Revisar Contratos"

    def test_task_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            task_get_selector(company=user.company, uuid=uuid4())

    def test_task_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        task_b = TaskFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            task_get_selector(company=user_a.company, uuid=task_b.uuid)

    def test_task_urgent_list_selector(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        today = date(2026, 8, 16)

        t_urgent = TaskFactory(
            wedding=wedding,
            due_date=today - timedelta(days=1),
            is_completed=False,
        )
        TaskFactory(
            wedding=wedding,
            due_date=today + timedelta(days=5),
            is_completed=False,
        )
        TaskFactory(
            wedding=wedding,
            due_date=today - timedelta(days=1),
            is_completed=True,
        )

        qs = task_urgent_list_selector(company=user.company, today=today)
        assert list(qs) == [t_urgent]


@pytest.mark.django_db
class TestEventSelectors:
    """Testes para event selectors."""

    def test_event_list_selector_multitenancy(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        EventFactory(wedding=wedding_a, title="Evento A")
        EventFactory(wedding=wedding_b, title="Evento B")

        qs_a = event_list_selector(company=user_a.company)
        assert qs_a.count() == 1
        ev_a = qs_a.first()
        assert ev_a is not None and ev_a.title == "Evento A"

        qs_b = event_list_selector(company=user_b.company)
        assert qs_b.count() == 1
        ev_b = qs_b.first()
        assert ev_b is not None and ev_b.title == "Evento B"

    def test_event_list_selector_filter_by_wedding_and_dates(self, user: Any) -> None:
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        now = timezone.now()

        e1 = EventFactory(
            wedding=wedding1,
            start_time=now + timedelta(days=2),
            title="Evento no Período",
        )
        EventFactory(
            wedding=wedding1,
            start_time=now + timedelta(days=20),
            title="Evento Fora",
        )
        EventFactory(
            wedding=wedding2,
            start_time=now + timedelta(days=2),
            title="Outro Casamento",
        )

        start_d = (now + timedelta(days=1)).date()
        end_d = (now + timedelta(days=5)).date()

        qs = event_list_selector(
            company=user.company,
            wedding_id=wedding1.uuid,
            start_date=start_d,
            end_date=end_d,
        )
        assert list(qs) == [e1]

    def test_event_get_selector_success(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Degustação")

        result = event_get_selector(company=user.company, uuid=event.uuid)
        assert result.uuid == event.uuid
        assert result.title == "Degustação"

    def test_event_get_selector_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            event_get_selector(company=user.company, uuid=uuid4())

    def test_event_get_selector_multitenancy_isolation(self) -> None:
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        event_b = EventFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            event_get_selector(company=user_a.company, uuid=event_b.uuid)
