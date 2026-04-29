import pytest

from apps.events.tests.factories import EventFactory
from apps.scheduler.models.appointment import Appointment
from apps.scheduler.services.appointments import AppointmentService
from apps.scheduler.tests.appointment_factories import AppointmentFactory


@pytest.mark.django_db
@pytest.mark.service
class TestAppointmentService:
    """Testes de lógica de negócio para o AppointmentService."""

    def test_create_appointment_success(self, user):
        """Domínio: Criação de compromisso vinculado ao casamento e planner."""
        event = EventFactory(company=user.company)
        data = {
            "event": event.uuid,
            "title": "Reunião de Alinhamento",
            "event_type": "MEETING",
            "start_time": "2026-10-10T10:00:00Z",
            "end_time": "2026-10-10T11:00:00Z",
        }

        appointment = AppointmentService.create(user=user, data=data)
        assert appointment.company == user.company
        assert appointment.event == event
        assert appointment.title == "Reunião de Alinhamento"

    def test_update_appointment_success(self, user):
        """Domínio: Atualização de campos do compromisso."""
        appointment = AppointmentFactory(event__company=user.company, title="Antigo")
        AppointmentService.update(instance=appointment, data={"title": "Novo"})
        assert appointment.title == "Novo"

    def test_delete_appointment_success(self, user):
        """Domínio: Deleção física do compromisso."""
        appointment = AppointmentFactory(event__company=user.company)
        AppointmentService.delete(instance=appointment)
        assert Appointment.objects.filter(uuid=appointment.uuid).count() == 0
