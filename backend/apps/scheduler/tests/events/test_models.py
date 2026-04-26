import pytest

from apps.scheduler.models.event import Event
from apps.scheduler.tests.factories import EventFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestEventModel:
    """Testes de integridade física do modelo Event."""

    def test_event_str(self):
        event = Event(title="Degustação de Doces")
        assert str(event) == "Degustação de Doces"

    def test_event_ordering(self):
        """Garante que a ordenação padrão é por start_time."""
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        e2 = EventFactory(start_time=now + timedelta(days=2))
        e1 = EventFactory(start_time=now + timedelta(days=1))

        qs = Event.objects.filter(id__in=[e1.id, e2.id])
        assert list(qs) == [e1, e2]
