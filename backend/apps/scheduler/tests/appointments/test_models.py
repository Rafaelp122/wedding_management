from datetime import timedelta
from typing import Any, cast

import pytest
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.tests.factories import EventFactory as _EventFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def EventFactory(*args: Any, **kwargs: Any) -> Event:
    return cast(Event, _EventFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestEventModelMetadata:
    """Testes de representação e metadados do modelo Event."""

    def test_event_str_is_title(self, user: Any) -> None:
        """__str__ deve retornar o título do evento."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Prova de Vestido")
        assert str(event) == "Prova de Vestido"

    def test_event_ordering_by_start_time(self, user: Any) -> None:
        """Ordenação padrão deve ser por start_time ascendente."""
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        e_late = EventFactory(wedding=wedding, start_time=now + timedelta(days=30))
        e_soon = EventFactory(wedding=wedding, start_time=now + timedelta(days=5))
        e_mid = EventFactory(wedding=wedding, start_time=now + timedelta(days=15))

        events = list(Event.objects.all())
        assert events[0] == e_soon
        assert events[1] == e_mid
        assert events[2] == e_late

    def test_event_end_time_defaults_hour_after_start(self, user: Any) -> None:
        """End_time padrão via factory é 1h após start_time."""
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=now,
            end_time=now + timedelta(hours=1),
        )
        event.full_clean()
        assert event.end_time == now + timedelta(hours=1)


@pytest.mark.django_db
class TestEventTypeChoices:
    """Testes dos tipos de evento disponíveis."""

    def test_event_type_meeting(self, user: Any) -> None:
        """Evento do tipo MEETING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.MEETING)
        event.full_clean()

    def test_event_type_payment(self, user: Any) -> None:
        """Evento do tipo PAYMENT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.PAYMENT)
        event.full_clean()

    def test_event_type_visit(self, user: Any) -> None:
        """Evento do tipo VISIT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.VISIT)
        event.full_clean()

    def test_event_type_tasting(self, user: Any) -> None:
        """Evento do tipo TASTING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.TASTING)
        event.full_clean()

    def test_event_type_default_is_other(self, user: Any) -> None:
        """Tipo padrão deve ser OTHER."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.event_type == Event.TypeChoices.OTHER


@pytest.mark.django_db
class TestEventReminder:
    """Testes das configurações de lembrete do Event."""

    def test_event_reminder_default_disabled(self, user: Any) -> None:
        """reminder_enabled deve ser False por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_enabled is False

    def test_event_reminder_minutes_default(self, user: Any) -> None:
        """reminder_minutes_before deve ser 60 por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_minutes_before == 60

    def test_event_recurrence_rule_choices(self, user: Any) -> None:
        """RecurrenceChoices contém os valores em português."""
        expected = {"none", "semanal", "quinzenal", "mensal"}
        assert set(Event.RecurrenceChoices.values) == expected
