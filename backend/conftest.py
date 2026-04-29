"""
Configuração Global de Testes (Pytest).
"""

from unittest.mock import patch

import factory
import pytest
from django.test import Client
from ninja_jwt.tokens import RefreshToken
from pytest_factoryboy import register

from apps.users.tests.factories import AdminFactory, UserFactory


# Desativa o signal de criação de budget para evitar conflitos nos testes
@pytest.fixture(autouse=True)
def mute_signals():
    with patch("apps.events.signals.handle_event_creation") as mock_signal:
        yield mock_signal


# 1. Registo Global de Factories
register(UserFactory)
register(AdminFactory)

# 2. Configuração do Faker para dados brasileiros reais
factory.Faker._DEFAULT_LOCALE = "pt_BR"


class JWTClient(Client):
    """Django test client that injects a Bearer JWT on every request."""

    def __init__(self, user=None, **kwargs):
        super().__init__(**kwargs)
        self._jwt_headers = {}
        if user is not None:
            refresh = RefreshToken.for_user(user)
            self._jwt_headers = {"HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}"}

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        **extra,
    ):
        extra = {**self._jwt_headers, **extra}
        return super().generic(
            method, path, data=data, content_type=content_type, secure=secure, **extra
        )


@pytest.fixture
def user(user_factory):
    """Cria e retorna um usuário ativo (Planner) para uso nos testes."""
    return user_factory.create(is_active=True)


@pytest.fixture
def auth_client(user):
    """
    Django test Client pré-configurado com JWT Bearer do usuário `user`.
    """
    c = JWTClient(user=user)
    c.user = user
    return c
