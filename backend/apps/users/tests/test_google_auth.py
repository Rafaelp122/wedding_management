"""
Testes para o fluxo de autenticação e registro via Google OAuth2.

Cobre:
- Autenticação de usuário existente com sucesso
- Provisionamento de novo usuário e empresa (tenant) com sucesso
- Tentativa de login com usuário inativo (401)
- Erro ao validar token inválido/expirado (ValueError -> 401)
- Validação de GOOGLE_CLIENT_ID ausente (401)
- Validação de e-mail não verificado (401)
- Truncamento de first_name longo (>150 caracteres)
- Integração via API Ninja no endpoint POST /api/v1/auth/google/
"""

from unittest.mock import patch

import pytest
from django.test import override_settings

from apps.core.exceptions import InvalidCredentialsError, InvalidTokenError
from apps.core.services.social_auth import GoogleOAuthProvider
from apps.users.models import User
from apps.users.services.google_auth_service import GoogleAuthService


pytestmark = pytest.mark.django_db


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_authenticate_with_google_existing_user(user_factory):
    """
    Testa a autenticação com sucesso para um usuário existente via Google OAuth.
    """
    existing_user = user_factory.create(email="existing@example.com")

    mock_id_info = {
        "email": "existing@example.com",
        "given_name": existing_user.first_name,
        "family_name": existing_user.last_name,
        "email_verified": True,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        result = GoogleAuthService.authenticate_with_google("valid_id_token")

    assert result.user.email == existing_user.email
    assert result.user.id == existing_user.id
    assert result.access is not None
    assert result.refresh is not None


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_authenticate_with_google_new_user():
    """
    Testa a criação de um novo usuário e empresa ao autenticar via Google OAuth.
    """
    mock_id_info = {
        "email": "newgoogleuser@example.com",
        "given_name": "Maria",
        "family_name": "Silva",
        "email_verified": True,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        result = GoogleAuthService.authenticate_with_google("valid_id_token")

    created_user = User.objects.get(email="newgoogleuser@example.com")
    assert created_user.is_active is True
    assert created_user.first_name == "Maria"
    assert created_user.last_name == "Silva"
    assert created_user.company is not None
    assert bool(created_user.company.name)

    assert result.user.email == "newgoogleuser@example.com"
    assert result.user.id == created_user.id
    assert result.access is not None
    assert result.refresh is not None


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_authenticate_with_google_inactive_user(user_factory):
    """
    Testa que a autenticação falha se a conta do usuário existente estiver inativa.
    """
    inactive_user = user_factory.create(email="inactive@example.com", is_active=False)

    mock_id_info = {
        "email": inactive_user.email,
        "given_name": inactive_user.first_name,
        "family_name": inactive_user.last_name,
        "email_verified": True,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        with pytest.raises(InvalidCredentialsError) as exc_info:
            GoogleAuthService.authenticate_with_google("valid_id_token")

    assert exc_info.value.status_code == 401
    assert "Credenciais inválidas ou conta desativada." in str(exc_info.value)


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_authenticate_with_google_invalid_token():
    """
    Testa se ValueError ao verificar o token é convertido em InvalidTokenError.
    """
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError("Token inválido"),
    ):
        with pytest.raises(InvalidTokenError) as exc_info:
            GoogleAuthService.authenticate_with_google("invalid_id_token")

    assert exc_info.value.status_code == 401
    assert "Token do Google inválido ou expirado." in str(exc_info.value)


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_google_oauth_provider_missing_client_id():
    """
    Testa que GoogleOAuthProvider gera InvalidCredentialsError
    quando GOOGLE_CLIENT_ID está ausente.
    """
    with override_settings(GOOGLE_CLIENT_ID=""):
        provider = GoogleOAuthProvider()
        with pytest.raises(InvalidCredentialsError) as exc_info:
            provider.verify_token("some_token")

    assert exc_info.value.status_code == 401
    assert "Configuração do Google OAuth ausente no servidor." in str(exc_info.value)


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_google_oauth_provider_email_not_verified():
    """
    Testa que GoogleOAuthProvider gera InvalidCredentialsError
    se email_verified for False ou estiver ausente.
    """
    mock_id_info = {
        "email": "unverified@example.com",
        "given_name": "João",
        "email_verified": False,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        provider = GoogleOAuthProvider()
        with pytest.raises(InvalidCredentialsError) as exc_info:
            provider.verify_token("unverified_token")

    assert exc_info.value.status_code == 401
    assert "E-mail do Google não verificado." in str(exc_info.value)

    # Testa chave ausente
    mock_id_info_missing = {
        "email": "unverified@example.com",
    }
    with patch(
        "google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info_missing
    ):
        provider2 = GoogleOAuthProvider()
        with pytest.raises(InvalidCredentialsError) as exc_info:
            provider2.verify_token("unverified_token")

    assert exc_info.value.status_code == 401
    assert "E-mail do Google não verificado." in str(exc_info.value)


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_google_oauth_provider_email_empty():
    """
    Testa que GoogleOAuthProvider gera InvalidCredentialsError
    se o e-mail estiver vazio.
    """
    mock_id_info = {
        "email_verified": True,
        "email": "",
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        provider = GoogleOAuthProvider()
        with pytest.raises(InvalidCredentialsError) as exc_info:
            provider.verify_token("token")

    assert exc_info.value.status_code == 401
    assert "não fornecido" in str(exc_info.value)


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_google_oauth_provider_long_given_name():
    """
    Testa que GoogleOAuthProvider trunca given_name com mais de 150 caracteres.
    """
    long_name = "A" * 200
    mock_id_info = {
        "email": "longname@example.com",
        "given_name": long_name,
        "family_name": "Sobrenome",
        "email_verified": True,
        "sub": "google_sub_123",
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        provider = GoogleOAuthProvider()
        user_info = provider.verify_token("token_long_name")

    assert len(user_info.first_name) == 150
    assert user_info.first_name == "A" * 150


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_mask_email_no_at():
    """Cobre o fallback da mascaração de email sem o @."""
    from apps.users.services.google_auth_service import _mask_email

    assert _mask_email("invalidemail") == "***"


def test_mask_email_short_name():
    """Cobre o fallback da mascaração com nomes de usuário muito curtos."""
    from apps.users.services.google_auth_service import _mask_email

    assert _mask_email("ab@example.com") == "a*@example.com"


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_api_google_login_success(auth_client, user_factory):
    """
    Testa o endpoint POST /api/v1/auth/google/ com payload válido via cliente API.
    """
    existing_user = user_factory.create(email="api_google@example.com")

    mock_id_info = {
        "email": "api_google@example.com",
        "given_name": existing_user.first_name,
        "family_name": existing_user.last_name,
        "email_verified": True,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        response = auth_client.post(
            "/api/v1/auth/google/",
            {"id_token": "valid_token_sample"},
            content_type="application/json",
        )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert data["user"]["email"] == "api_google@example.com"


@override_settings(GOOGLE_CLIENT_ID="test_client_id")
def test_api_google_login_invalid_token(auth_client):
    """
    Testa o endpoint POST /api/v1/auth/google/ com token inválido retornando 401.
    """
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError("Bad token"),
    ):
        response = auth_client.post(
            "/api/v1/auth/google/",
            {"id_token": "invalid_token_sample"},
            content_type="application/json",
        )

    assert response.status_code == 401


def test_authenticate_with_google_dependency_injection():
    """
    Testa a injeção de dependência do OAuthProvider no GoogleAuthService
    sem depender de mocks de biblioteca externa.
    """
    from apps.core.services.social_auth import OAuthUserInfo

    class StubOAuthProvider:
        def verify_token(self, token: str) -> OAuthUserInfo:
            return OAuthUserInfo(
                email="di_stub@example.com",
                email_verified=True,
                first_name="DI",
                last_name="Stub",
                sub="12345",
            )

    result = GoogleAuthService.authenticate_with_google(
        "dummy_token", provider=StubOAuthProvider()
    )

    assert result.user.email == "di_stub@example.com"
    assert result.user.first_name == "DI"
    assert User.objects.filter(email="di_stub@example.com").exists()
