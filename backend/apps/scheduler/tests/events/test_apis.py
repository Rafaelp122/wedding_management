import pytest


@pytest.mark.django_db
@pytest.mark.api
class TestEventAPI:
    """Testes de integração para a API de Eventos - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_events_isolation(self, auth_client, scheduler_seed):
        """Garante que um planner só vê eventos dos seus casamentos."""
        response = auth_client.get("/api/v1/scheduler/events/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Reunião A"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_event_forbidden(self, auth_client, scheduler_seed):
        """Segurança: Não pode acessar evento de outro planner."""
        other_event = scheduler_seed["other_event"]
        response = auth_client.get(f"/api/v1/scheduler/events/{other_event.uuid}/")
        assert response.status_code == 404

    def test_create_event_validates_dates(self, auth_client, scheduler_seed):
        """Valida regras de negócio de tempo na criação."""
        my_wedding = scheduler_seed["my_event"].wedding

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

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_event_isolation(self, auth_client, scheduler_seed):
        """Segurança: Não pode editar evento de outro planner."""
        other_event = scheduler_seed["other_event"]
        response = auth_client.patch(
            f"/api/v1/scheduler/events/{other_event.uuid}/",
            data={"title": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_event_isolation(self, auth_client, scheduler_seed):
        """Segurança: Não pode deletar evento de outro planner."""
        other_event = scheduler_seed["other_event"]
        response = auth_client.delete(f"/api/v1/scheduler/events/{other_event.uuid}/")
        assert response.status_code == 404
