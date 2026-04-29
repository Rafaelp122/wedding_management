"""
Configuração Local de Testes: App Scheduler.
"""

import pytest
from pytest_factoryboy import register

from apps.events.tests.factories import EventFactory

from .appointment_factories import AppointmentFactory, MeetingFactory, TaskFactory


# Registo das factories como fixtures (ex: event_factory)
register(AppointmentFactory)
register(MeetingFactory)
register(TaskFactory)


@pytest.fixture
def scheduler_seed(db, user):
    """
    Cenário completo de isolamento do cronograma (Multitenancy).
    Cria dados para o usuário autenticado e para um usuário alheio.
    """
    # Evento do Meu Tenant (User já deve ter uma company vinculada)
    my_event = EventFactory(company=user.company)
    my_appointment = AppointmentFactory(
        event=my_event,
        title="Reunião A",
        event_type="MEETING",
    )

    # Dados de outro Planner (Tenant Isolado)
    other_appointment = AppointmentFactory(title="Compromisso Alheio")

    return {
        "my_event": my_event,
        "my_appointment": my_appointment,
        "other_appointment": other_appointment,
    }
