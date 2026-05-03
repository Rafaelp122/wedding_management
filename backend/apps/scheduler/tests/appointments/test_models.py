from datetime import timedelta

import pytest
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.tests.factories import EventFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestEventModelMetadata:
    """Testes de representação e metadados do modelo Event."""

    def test_event_str_is_title(self, user):
        """__str__ deve retornar o título do evento."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Prova de Vestido")
        assert str(event) == "Prova de Vestido"

    def test_event_ordering_by_start_time(self, user):
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

    def test_event_end_time_defaults_hour_after_start(self, user):
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

    def test_event_type_meeting(self, user):
        """Evento do tipo MEETING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.MEETING)
        event.full_clean()

    def test_event_type_payment(self, user):
        """Evento do tipo PAYMENT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.PAYMENT)
        event.full_clean()

    def test_event_type_visit(self, user):
        """Evento do tipo VISIT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.VISIT)
        event.full_clean()

    def test_event_type_tasting(self, user):
        """Evento do tipo TASTING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.TASTING)
        event.full_clean()

    def test_event_type_default_is_other(self, user):
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

    def test_event_reminder_default_disabled(self, user):
        """reminder_enabled deve ser False por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_enabled is False

    def test_event_reminder_minutes_default(self, user):
        """reminder_minutes_before deve ser 60 por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_minutes_before == 60
