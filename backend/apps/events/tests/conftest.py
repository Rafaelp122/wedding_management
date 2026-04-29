"""
Configuração Local de Testes: App Events.

Este ficheiro regista as factories de casamentos como fixtures do Pytest.
As fixtures definidas aqui permitem a criação rápida de ambientes isolados
para testar logística, finanças e agenda.
"""

from datetime import timedelta

import pytest
from django.utils import timezone
from pytest_factoryboy import register

from apps.events.tests.factories import (
    CompletedEventFactory,
    EventFactory,
    WeddingFactory,
)


# Regista as factories como fixtures injetáveis (ex: event_factory)
register(EventFactory)
register(WeddingFactory)
register(CompletedEventFactory)


@pytest.fixture
def event(db, wedding_factory):
    """
    Fixture que devolve um casamento ativo pronto para uso nos testes.
    """
    return wedding_factory.create()


@pytest.fixture
def event_payload():
    """
    Retorna um dicionário que simula exatamente o JSON enviado pelo Frontend para Casamentos.
    """
    return {
        "name": "Casamento de Teste Payload",
        "event_type": "WEDDING",
        "date": (timezone.now() + timedelta(days=60)).date(),
        "location": "Espaço Alvorada, SP",
        "expected_guests": 150,
        "wedding_detail": {
            "bride_name": "Maria Silva",
            "groom_name": "João Souza",
        },
    }
