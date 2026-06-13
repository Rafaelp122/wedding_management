import pytest
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.tests.factories import EventFactory, TaskFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestSchedulerEventsAPI:
    """Testes dos endpoints de Eventos do Scheduler."""

    def test_list_events_isolation(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        EventFactory(wedding=wedding, title="Reunião A")
        EventFactory(title="Reunião B")

        response = auth_client.get("/api/v1/scheduler/events/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Reunião A"

    def test_list_events_unauthorized(self, client):
        response = client.get("/api/v1/scheduler/events/")
        assert response.status_code == 401

    def test_create_event_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        now = timezone.now()

        response = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(wedding.uuid),
                "title": "Prova de Buffet",
                "event_type": "degustacao",
                "location": "",
                "description": "",
                "start_time": (now + timezone.timedelta(days=10)).isoformat(),
                "end_time": (now + timezone.timedelta(days=10, hours=1)).isoformat(),
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Prova de Buffet"

    def test_create_event_unauthorized(self, client):
        response = client.post(
            "/api/v1/scheduler/events/", {}, content_type="application/json"
        )
        assert response.status_code == 401

    def test_create_event_invalid_end_time(self, auth_client, user):
        """end_time < start_time deve retornar 422."""
        wedding = WeddingFactory(company=user.company)
        now = timezone.now()

        response = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(wedding.uuid),
                "title": "Inválido",
                "event_type": "outro",
                "location": "",
                "description": "",
                "start_time": (now + timezone.timedelta(days=1, hours=12)).isoformat(),
                "end_time": (now + timezone.timedelta(days=1, hours=10)).isoformat(),
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_event_negative_reminder(self, auth_client, user):
        """reminder_minutes_before < 0 deve retornar 422."""
        wedding = WeddingFactory(company=user.company)
        now = timezone.now()

        response = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(wedding.uuid),
                "title": "Inválido",
                "event_type": "outro",
                "location": "",
                "description": "",
                "start_time": (now + timezone.timedelta(days=1, hours=12)).isoformat(),
                "end_time": (now + timezone.timedelta(days=1, hours=14)).isoformat(),
                "reminder_minutes_before": -10,
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_payment_event_manual_returns_422(self, auth_client, user):
        """BR-S01: eventos de pagamento não podem ser criados manualmente."""
        wedding = WeddingFactory(company=user.company)
        now = timezone.now()

        response = auth_client.post(
            "/api/v1/scheduler/events/",
            {
                "wedding": str(wedding.uuid),
                "title": "Pagamento Manual",
                "event_type": "pagamento",
                "location": "",
                "description": "",
                "start_time": (now + timezone.timedelta(days=1)).isoformat(),
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_retrieve_event_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        event = EventFactory(wedding=wedding, title="Prova de Vestido")

        response = auth_client.get(f"/api/v1/scheduler/events/{event.uuid}/")
        assert response.status_code == 200
        assert response.json()["title"] == "Prova de Vestido"

    def test_retrieve_event_isolation_404(self, auth_client):
        other_event = EventFactory(title="Evento Alheio")

        response = auth_client.get(f"/api/v1/scheduler/events/{other_event.uuid}/")
        assert response.status_code == 404

    def test_update_event_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        event = EventFactory(wedding=wedding, title="Antigo")

        response = auth_client.patch(
            f"/api/v1/scheduler/events/{event.uuid}/",
            {"title": "Novo Título"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Novo Título"

    def test_update_event_unauthorized(self, client):
        response = client.patch(
            "/api/v1/scheduler/events/00000000-0000-0000-0000-000000000001/",
            {},
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_update_event_isolation_404(self, auth_client):
        other_event = EventFactory()

        response = auth_client.patch(
            f"/api/v1/scheduler/events/{other_event.uuid}/",
            {"title": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_update_event_does_not_overwrite_recurrence_rule(self, auth_client, user):
        """PATCH de evento sem recurrence_rule não deve alterar a regra existente."""
        wedding = WeddingFactory(company=user.company)
        event = EventFactory(
            wedding=wedding,
            title="Antigo",
            recurrence_rule=Event.RecurrenceChoices.WEEKLY,
        )

        response = auth_client.patch(
            f"/api/v1/scheduler/events/{event.uuid}/",
            {"title": "Novo Título"},
            content_type="application/json",
        )
        assert response.status_code == 200

        event.refresh_from_db()
        assert event.recurrence_rule == Event.RecurrenceChoices.WEEKLY

    def test_delete_event_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        event = EventFactory(wedding=wedding)

        response = auth_client.delete(f"/api/v1/scheduler/events/{event.uuid}/")
        assert response.status_code == 204

    def test_delete_event_unauthorized(self, client):
        response = client.delete(
            "/api/v1/scheduler/events/00000000-0000-0000-0000-000000000001/"
        )
        assert response.status_code == 401

    def test_delete_event_isolation_404(self, auth_client):
        other_event = EventFactory()

        response = auth_client.delete(f"/api/v1/scheduler/events/{other_event.uuid}/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestSchedulerTasksAPI:
    """Testes dos endpoints de Tarefas do Scheduler."""

    def test_list_tasks_isolation(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        TaskFactory(wedding=wedding, title="Minha Tarefa")
        TaskFactory(title="Tarefa Alheia")

        response = auth_client.get("/api/v1/scheduler/tasks/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Minha Tarefa"

    def test_list_tasks_unauthorized(self, client):
        response = client.get("/api/v1/scheduler/tasks/")
        assert response.status_code == 401

    def test_create_task_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)

        response = auth_client.post(
            "/api/v1/scheduler/tasks/",
            {
                "wedding": str(wedding.uuid),
                "title": "Contratar Buffet",
                "description": "Pedir 3 orçamentos",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Contratar Buffet"

    def test_create_task_unauthorized(self, client):
        response = client.post(
            "/api/v1/scheduler/tasks/", {}, content_type="application/json"
        )
        assert response.status_code == 401

    def test_update_task_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        task = TaskFactory(wedding=wedding, title="Antigo", is_completed=False)

        response = auth_client.patch(
            f"/api/v1/scheduler/tasks/{task.uuid}/",
            {"title": "Novo", "is_completed": True},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Novo"
        assert data["is_completed"] is True

    def test_update_task_unauthorized(self, client):
        response = client.patch(
            "/api/v1/scheduler/tasks/00000000-0000-0000-0000-000000000001/",
            {},
            content_type="application/json",
        )
        assert response.status_code == 401

    def test_delete_task_success(self, auth_client, user):
        wedding = WeddingFactory(company=user.company)
        task = TaskFactory(wedding=wedding)

        response = auth_client.delete(f"/api/v1/scheduler/tasks/{task.uuid}/")
        assert response.status_code == 204

    def test_delete_task_unauthorized(self, client):
        response = client.delete(
            "/api/v1/scheduler/tasks/00000000-0000-0000-0000-000000000001/"
        )
        assert response.status_code == 401

    def test_delete_task_isolation_404(self, auth_client):
        other_task = TaskFactory()

        response = auth_client.delete(f"/api/v1/scheduler/tasks/{other_task.uuid}/")
        assert response.status_code == 404
