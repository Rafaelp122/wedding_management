"""
Configuração Local de Testes: App Scheduler.

Regista as factories do calendário para uso como fixtures pytest.
"""

from pytest_factoryboy import register

from .factories import EventFactory, MeetingFactory, TaskFactory


register(EventFactory)
register(MeetingFactory)
register(TaskFactory)
