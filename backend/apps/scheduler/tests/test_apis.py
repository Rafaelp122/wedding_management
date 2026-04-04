import pytest

from apps.scheduler.services import EventService
from apps.weddings.services import WeddingService


@pytest.fixture
def seed_data(user, django_user_model):
    # Planner alvo
    my_wedding = WeddingService.create(
        user,
        {
            "bride_name": "Minha",
            "groom_name": "Noz",
            "location": "A",
            "date": "2026-10-11",
        },
    )
    my_event = EventService.create(
        user,
        {
            "wedding": my_wedding,
            "title": "Reunião A",
            "event_type": "reuniao",
            "start_time": "2026-10-11T10:00:00Z",
            "end_time": "2026-10-11T11:00:00Z",
        },
    )

    # Planner alheio
    other_user = django_user_model.objects.create_user(email="b@b.com", password="123")
    other_wedding = WeddingService.create(
        other_user,
        {
            "bride_name": "Outra",
            "groom_name": "Outro",
            "location": "B",
            "date": "2026-10-11",
        },
    )
    EventService.create(
        other_user,
        {
            "wedding": other_wedding,
            "title": "Reunião B",
            "event_type": "reuniao",
            "start_time": "2026-10-11T12:00:00Z",
            "end_time": "2026-10-11T13:00:00Z",
        },
    )

    return {
        "my_event": my_event,
    }


@pytest.mark.django_db
class TestSchedulerNinjaAPI:
    def test_list_events_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/scheduler/events/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Reunião A"

    def test_create_event_validates_dates(self, auth_client, seed_data):
        my_wedding = seed_data["my_event"].wedding

        # 1. end_time before start_time
        response = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(my_wedding.uuid),
                "title": "Inválido",
                "event_type": "outro",
                "start_time": "2026-10-10T12:00:00Z",
                "end_time": "2026-10-10T10:00:00Z",
                "reminder_minutes_before": 10,
            },
            content_type="application/json",
        )
        assert response.status_code == 422
        errors = response.json().get("detail", [])
        assert "A hora de término não pode ser anterior à hora de início." in str(
            errors
        )

        # 2. reminder_minutes_before negative
        response2 = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(my_wedding.uuid),
                "title": "Inválido 2",
                "event_type": "outro",
                "start_time": "2026-10-10T12:00:00Z",
                "end_time": "2026-10-10T14:00:00Z",
                "reminder_minutes_before": -10,
            },
            content_type="application/json",
        )
        assert response2.status_code == 422
        errors2 = response2.json().get("detail", [])
        assert "Os minutos do lembrete devem ser um valor positivo." in str(errors2)
