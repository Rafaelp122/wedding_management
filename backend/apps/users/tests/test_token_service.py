"""
Testes unitários para o TokenService.

Cobre os métodos:
- TokenService.obtain() — via conftest já existente
- TokenService.refresh() — refresh de token
- TokenService.verify() — verificação de token

Regra: toda função pública em services.py deve ter ≥1 teste de sucesso
e ≥1 teste de falha.
"""

import pytest
from ninja.errors import HttpError
from ninja_jwt.schema import TokenRefreshOutputSchema
from ninja_jwt.tokens import RefreshToken

from apps.users.schemas import TokenOut, UserDataOut, VerifyTokenOut
from apps.users.services.token_service import TokenService


pytestmark = pytest.mark.django_db


class TestTokenServiceObtain:
    """Testes para TokenService.obtain()."""

    def test_obtain_success(self, user_factory):
        """Credenciais válidas retornam TokenOut com access + refresh."""
        user_factory.create(
            email="auth@example.com", password="secure123", is_active=True
        )

        result = TokenService.obtain("auth@example.com", "secure123")

        assert isinstance(result, TokenOut)
        assert isinstance(result.user, UserDataOut)
        assert result.access
        assert result.refresh
        assert result.user.email == "auth@example.com"

    def test_obtain_wrong_password_raises_401(self, user_factory):
        """Senha incorreta levanta HttpError 401."""
        user_factory.create(
            email="auth@example.com", password="secure123", is_active=True
        )

        with pytest.raises(HttpError) as exc_info:
            TokenService.obtain("auth@example.com", "wrong")

        assert exc_info.value.status_code == 401

    def test_obtain_inactive_user_raises_401(self, user_factory):
        """Usuário inativo levanta HttpError 401."""
        user_factory.create(
            email="inactive@example.com", password="secure123", is_active=False
        )

        with pytest.raises(HttpError) as exc_info:
            TokenService.obtain("inactive@example.com", "secure123")

        assert exc_info.value.status_code == 401


class TestTokenServiceRefresh:
    """Testes para TokenService.refresh()."""

    def test_refresh_success(self, user_factory):
        """Refresh com token válido retorna TokenRefreshOutputSchema."""
        user = user_factory.create(is_active=True)
        refresh = RefreshToken.for_user(user)

        result = TokenService.refresh(str(refresh))

        assert isinstance(result, TokenRefreshOutputSchema)
        assert result.access is not None
        assert result.refresh is not None
        # Com rotação ativa, o novo refresh deve ser diferente do original
        assert result.refresh != str(refresh)

    def test_refresh_invalid_token_raises_error(self):
        """Refresh com token inválido levanta HttpError 401."""
        with pytest.raises(HttpError) as exc_info:
            TokenService.refresh("invalid.token.string")

        assert exc_info.value.status_code == 401


class TestTokenServiceVerify:
    """Testes para TokenService.verify()."""

    def test_verify_success(self, user_factory):
        """Verificação de access token válido retorna VerifyTokenOut."""
        user = user_factory.create(is_active=True)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        result = TokenService.verify(access_token)

        assert isinstance(result, VerifyTokenOut)

    def test_verify_invalid_token_raises_error(self):
        """Verificação de token inválido levanta HttpError 401."""
        with pytest.raises(HttpError) as exc_info:
            TokenService.verify("invalid.token.here")

        assert exc_info.value.status_code == 401
