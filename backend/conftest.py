"""
Configuração Global de Testes (Pytest).

Este ficheiro define as infraestruturas base para todo o ecossistema do projeto:
- Configuração do Faker para Português (Brasil).
- Registo Global de Factories (User/Admin) para suporte ao Multitenancy.
- Fixtures de Cliente de API (Base e Autenticado via JWT).

As factories de User são registadas aqui porque quase todas as entidades do sistema
(Weddings, Expenses, Contracts) dependem de um utilizador (Planner).
"""

import factory
import pytest
from pytest_factoryboy import register
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

# Importação das factories para registo global
from apps.users.tests.factories import AdminFactory, UserFactory


# 1. Registo Global de Factories
# Ao registar aqui, 'user_factory' e 'admin_factory' tornam-se fixtures
# disponíveis em qualquer teste de qualquer app do projeto.
register(UserFactory)
register(AdminFactory)

# 2. Configuração do Faker para dados brasileiros reais
# Garante que nomes, endereços e textos gerados sigam o padrão pt_BR.
factory.Faker._DEFAULT_LOCALE = "pt_BR"


@pytest.fixture
def api_client():
    """
    Retorna um cliente de API do DRF não autenticado.
    Útil para testar permissões de acesso (401 Unauthorized / 403 Forbidden).
    """
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user_factory):
    """
    Retorna um cliente de API autenticado com um Token JWT real.

    Esta fixture automatiza o fluxo de:
    1. Criar um utilizador (Planner) via user_factory.
    2. Gerar o par de tokens JWT (Access/Refresh).
    3. Configurar o header 'Authorization: Bearer <token>'.

    Uso:
        def test_minha_view(authenticated_client):
            response = authenticated_client.get('/api/rota/')
            # O utilizador está disponível em authenticated_client.user
    """
    # Cria o utilizador usando a factory registada globalmente
    user = user_factory.create()

    # Gera os tokens JWT conforme configurado no SimpleJWT
    refresh = RefreshToken.for_user(user)

    # Configura o cabeçalho padrão para todas as requisições deste cliente
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    # Atacha o objeto user ao cliente para facilitar asserções nos testes
    api_client.user = user

    return api_client
