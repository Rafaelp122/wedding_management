"""
Configuração Local de Testes: App Weddings.

Este ficheiro regista as factories de casamentos como fixtures do Pytest.
As fixtures definidas aqui permitem a criação rápida de ambientes isolados
para testar logística, finanças e agenda.

Nota: Se outros apps (como finances) precisarem criar casamentos com frequência,
considere mover o registo das factories para o conftest.py da raiz.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from pytest_factoryboy import register

from apps.weddings.tests.factories import CompletedWeddingFactory, WeddingFactory


# Regista as factories como fixtures injetáveis (ex: wedding_factory)
register(WeddingFactory)
register(CompletedWeddingFactory)


@pytest.fixture
def wedding(db, wedding_factory):
    """
    Fixture que devolve um casamento ativo pronto para uso nos testes.

    Já inclui um Planner autenticável e dados iniciais válidos, poupando
    o setup manual em cada teste de integração.
    """
    return wedding_factory.create()


@pytest.fixture
def wedding_payload():
    """
    Retorna um dicionário que simula exatamente o JSON enviado pelo Frontend.
    Este é o contrato real da API.
    """
    return {
        "bride_name": "Maria Silva",
        "groom_name": "João Souza",
        "date": (timezone.now() + timedelta(days=60)).date(),
        "location": "Espaço Alvorada, SP",
        "expected_guests": 150,
        "total_estimated": Decimal("50000.00"),
    }
