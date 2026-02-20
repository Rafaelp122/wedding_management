"""
Configuração Local de Testes: App Weddings.

Este ficheiro regista as factories de casamentos como fixtures do Pytest.
As fixtures definidas aqui permitem a criação rápida de ambientes isolados
para testar logística, finanças e agenda.

Nota: Se outros apps (como finances) precisarem criar casamentos com frequência,
considere mover o registo das factories para o conftest.py da raiz.
"""

import pytest
from pytest_factoryboy import register

from .model_factories import CompletedWeddingFactory, WeddingFactory


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
