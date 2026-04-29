import pytest


@pytest.mark.django_db
@pytest.mark.api
class TestAppointmentAPI:
    """
    Testes de integração para a API de Compromissos.
    Conforme TESTING_STANDARDS.md.
    """

    @pytest.mark.multitenancy
    def test_list_appointments_isolation(self, auth_client, scheduler_seed):
        """Garante que um planner só vê compromissos dos seus casamentos."""
        response = auth_client.get("/api/v1/scheduler/appointments/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "Reunião A"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_appointment_forbidden(self, auth_client, scheduler_seed):
        """Segurança: Não pode acessar compromisso de outro planner."""
        other_appointment = scheduler_seed["other_appointment"]
        response = auth_client.get(
            f"/api/v1/scheduler/appointments/{other_appointment.uuid}/"
        )
        assert response.status_code == 404

    def test_create_appointment_validates_dates(self, auth_client, scheduler_seed):
        """Valida regras de negócio de tempo na criação."""
        my_event = scheduler_seed["my_event"]

        # 1. end_time before start_time
        response = auth_client.post(
            "/api/v1/scheduler/appointments/",
            {
                "event": str(my_event.uuid),
                "title": "Inválido",
                "event_type": "OTHER",
                "start_time": "2026-10-10T12:00:00Z",
                "end_time": "2026-10-10T10:00:00Z",
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_appointment_isolation(self, auth_client, scheduler_seed):
        """Segurança: Não pode editar compromisso de outro planner."""
        other_appointment = scheduler_seed["other_appointment"]
        response = auth_client.patch(
            f"/api/v1/scheduler/appointments/{other_appointment.uuid}/",
            data={"title": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_appointment_isolation(self, auth_client, scheduler_seed):
        """Segurança: Não pode deletar compromisso de outro planner."""
        other_appointment = scheduler_seed["other_appointment"]
        response = auth_client.delete(
            f"/api/v1/scheduler/appointments/{other_appointment.uuid}/"
        )
        assert response.status_code == 404
