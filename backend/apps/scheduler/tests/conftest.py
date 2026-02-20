"""
Configuração Local de Testes: App Scheduler.

Este ficheiro regista as factories do calendário e define fixtures para
testar a agenda do Planner.
"""

import pytest
from pytest_factoryboy import register

# Mantendo as importações relativas como solicitado
from .model_factories import EventFactory, MeetingFactory


# Registo das factories como fixtures (ex: event_factory)
register(EventFactory)
register(MeetingFactory)


@pytest.fixture
def upcoming_meeting(db, meeting_factory):
    """Fixture que devolve uma reunião agendada para o futuro próximo."""
    return meeting_factory.create()


@pytest.fixture
def event_with_reminder(db, event_factory):
    """Fixture de um evento com lembrete ativo para testar disparos de notificação."""
    return event_factory.create(reminder_enabled=True, reminder_minutes_before=30)
