"""
Configuração Global de Testes (Pytest).
"""

from typing import Any, cast

import factory
import pytest
from django.http import HttpResponseBase
from django.test import Client
from ninja_jwt.tokens import RefreshToken
from pytest_factoryboy import register

from apps.users.models import User
from apps.users.tests.factories import AdminFactory, UserFactory


# 1. Registo Global de Factories
register(UserFactory)
register(AdminFactory)

# 2. Configuração do Faker para dados brasileiros reais
factory.Faker._DEFAULT_LOCALE = "pt_BR"  # type: ignore[attr-defined]


class JWTClient(Client):
    """Django test client that injects a Bearer JWT on every request."""

    user: User | None

    def __init__(self, user: User | None = None, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._jwt_headers = {}
        if user is not None:
            refresh = RefreshToken.for_user(user)  # type: ignore[misc]
            self._jwt_headers = {"HTTP_AUTHORIZATION": f"Bearer {refresh.access_token}"}

    def generic(  # type: ignore[override]
        self,
        method: str,
        path: str,
        data: Any = "",
        content_type: str = "application/octet-stream",
        secure: bool = False,
        **extra: Any,
    ) -> HttpResponseBase:
        extra = {**self._jwt_headers, **extra}
        return super().generic(
            method, path, data=data, content_type=content_type, secure=secure, **extra
        )


@pytest.fixture
def user(user_factory: Any) -> User:
    """Cria e retorna um usuário ativo (Planner) para uso nos testes."""
    return cast(User, user_factory.create(is_active=True))


@pytest.fixture
def auth_client(user: User) -> JWTClient:
    """
    Django test Client pré-configurado com JWT Bearer do usuário `user`.
    """
    c = JWTClient(user=user)
    c.user = user
    return c
