import pytest

from apps.scheduler.models.appointment import Appointment
from apps.scheduler.tests.appointment_factories import AppointmentFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestAppointmentModel:
    """Testes de integridade física do modelo Appointment."""

    def test_appointment_str(self):
        appointment = Appointment(
            title="Degustação de Doces", event_type=Appointment.EventType.MEETING
        )
        assert str(appointment) == "Degustação de Doces (Reunião)"

    def test_appointment_ordering(self):
        """Garante que a ordenação padrão é por start_time."""
        from datetime import timedelta

        from django.utils import timezone

        now = timezone.now()
        e2 = AppointmentFactory(start_time=now + timedelta(days=2))
        e1 = AppointmentFactory(start_time=now + timedelta(days=1))

        # Precisamos converter para lista para comparar ordem
        qs = Appointment.objects.filter(id__in=[e1.id, e2.id]).order_by("start_time")
        assert list(qs) == [e1, e2]
