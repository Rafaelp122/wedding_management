"""
Configuração Local de Testes: App Users.

Este ficheiro contém fixtures específicas para o domínio de utilizadores.
As factories 'UserFactory' e 'AdminFactory' foram movidas para o registo global
na raiz do backend para permitir que o cliente autenticado (JWT) funcione em
todos os módulos do sistema.
"""

import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache_between_tests():
    """Garante que o cache de rate limiting é limpo antes de cada teste."""
    cache.clear()


@pytest.fixture
def planner(db, user_factory):
    """
    Retorna uma instância de usuário (Planner) salva no banco.

    Esta fixture utiliza a 'user_factory' que foi registada globalmente
    no conftest da raiz. É um atalho útil para testes que precisam apenas
    de um objeto User sem a complexidade do cliente API.
    """
    return user_factory.create()


@pytest.fixture
def inactive_planner(db, user_factory):
    """Retorna um Planner inativo para testes de validação de conta."""
    return user_factory.create(is_active=False)
