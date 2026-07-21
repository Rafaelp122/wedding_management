"""
Testes para o fluxo de autenticação e registro via Google OAuth2.

Cobre:
- Autenticação de usuário existente com sucesso (sucesso no serviço)
- Provisionamento de novo usuário e empresa (tenant) com sucesso
- Tentativa de login com usuário inativo (401)
- Erro ao validar token inválido/expirado (ValueError -> 401)
- Erro ao receber token sem e-mail (401)
- Integração via API Ninja no endpoint POST /api/v1/auth/google/
"""

from unittest.mock import patch

import pytest
from ninja.errors import HttpError

from apps.users.models import User
from apps.users.services.google_auth_service import GoogleAuthService


pytestmark = pytest.mark.django_db


def test_authenticate_with_google_existing_user(user_factory):
    """
    Testa a autenticação com sucesso para um usuário existente via Google OAuth.
    """
    existing_user = user_factory.create(email="existing@example.com")

    mock_id_info = {
        "email": "existing@example.com",
        "given_name": existing_user.first_name,
        "family_name": existing_user.last_name,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        result = GoogleAuthService.authenticate_with_google("valid_id_token")

    assert result.user.email == existing_user.email
    assert result.user.id == existing_user.id
    assert result.access is not None
    assert result.refresh is not None


def test_authenticate_with_google_new_user():
    """
    Testa a criação de um novo usuário e empresa ao autenticar via Google OAuth.
    """
    mock_id_info = {
        "email": "newgoogleuser@example.com",
        "given_name": "Maria",
        "family_name": "Silva",
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        result = GoogleAuthService.authenticate_with_google("valid_id_token")

    created_user = User.objects.get(email="newgoogleuser@example.com")
    assert created_user.is_active is True
    assert created_user.first_name == "Maria"
    assert created_user.last_name == "Silva"
    assert created_user.company is not None
    assert "Workspace de Maria Silva" in created_user.company.name

    assert result.user.email == "newgoogleuser@example.com"
    assert result.user.id == created_user.id
    assert result.access is not None
    assert result.refresh is not None


def test_authenticate_with_google_inactive_user(user_factory):
    """
    Testa que a autenticação falha se a conta do usuário existente estiver inativa.
    """
    inactive_user = user_factory.create(email="inactive@example.com", is_active=False)

    mock_id_info = {
        "email": inactive_user.email,
        "given_name": inactive_user.first_name,
        "family_name": inactive_user.last_name,
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        with pytest.raises(HttpError) as exc_info:
            GoogleAuthService.authenticate_with_google("valid_id_token")

    assert exc_info.value.status_code == 401
    assert "Credenciais inválidas ou conta desativada." in str(exc_info.value)


def test_authenticate_with_google_invalid_token():
    """
    Testa se ValueError ao verificar o token é convertido em HttpError 401.
    """
    with patch(
        "google.oauth2.id_token.verify_oauth2_token",
        side_effect=ValueError("Token inválido"),
    ):
        with pytest.raises(HttpError) as exc_info:
            GoogleAuthService.authenticate_with_google("invalid_id_token")

    assert exc_info.value.status_code == 401
    assert "Token do Google inválido ou expirado." in str(exc_info.value)


def test_authenticate_with_google_missing_email():
    """
    Testa se o token sem e-mail resulta em HttpError 401.
    """
    mock_id_info = {
        "given_name": "NoEmail",
    }

    with patch("google.oauth2.id_token.verify_oauth2_token", return_value=mock_id_info):
        with pytest.raises(HttpError) as exc_info:
            GoogleAuthService.authenticate_with_google("token_without_email")

    assert exc_info.value.status_code == 401
    assert "Token do Google inválido ou expirado." in str(exc_info.value)


def test_api_google_login_success(auth_client, user_factory):
    """
    Testa o endpoint POST /api/v1/auth/google/ com payload válido via cliente API.
    """
    existing_user = user_factory.create(email="api_google@example.com")

    mock_id_info = {
        "email": "api_google@example.com",
        "given_name": existing_user.first_name,
        "family_name": existing_user.last_name,
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
