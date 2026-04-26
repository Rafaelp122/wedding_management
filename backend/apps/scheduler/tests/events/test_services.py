import pytest

from apps.scheduler.models.event import Event
from apps.scheduler.services.events import EventService
from apps.scheduler.tests.factories import EventFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestEventService:
    """Testes de lógica de negócio para o EventService."""

    def test_create_event_success(self, user):
        """Domínio: Criação de evento vinculado ao casamento e planner."""
        wedding = WeddingFactory(planner=user)
        data = {
            "wedding": wedding.uuid,
            "title": "Reunião de Alinhamento",
            "event_type": "reuniao",
            "start_time": "2026-10-10T10:00:00Z",
        }

        event = EventService.create(user=user, data=data)
        assert event.planner == user
        assert event.wedding == wedding
        assert event.title == "Reunião de Alinhamento"

    def test_update_event_success(self, user):
        """Domínio: Atualização de campos do evento."""
        event = EventFactory(wedding__planner=user, title="Antigo")
        EventService.update(instance=event, data={"title": "Novo"})
        assert event.title == "Novo"

    def test_delete_event_success(self, user):
        """Domínio: Deleção física do evento."""
        event = EventFactory(wedding__planner=user)
        EventService.delete(instance=event)
        assert Event.objects.filter(uuid=event.uuid).count() == 0
