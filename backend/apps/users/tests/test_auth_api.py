"""
Testes de regressão para os endpoints JWT (obtain, refresh, verify).

Cobre:
- Obtenção de token com credenciais válidas (200)
- Obtenção de token com senha inválida (401)
- Obtenção de token com usuário inativo (401)
- Refresh de token bem-sucedido com rotação (200)
- Reuso de refresh token após rotação (401)
- Verificação de token válido (200)
- Verificação de token inválido (401)
"""

import pytest


pytestmark = pytest.mark.django_db


def test_obtain_token_success(auth_client, user):
    """POST /api/v1/auth/token/ com credenciais válidas retorna 200 com tokens."""
    response = auth_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "password123"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    assert "user" in data
    assert data["user"]["email"] == user.email


def test_obtain_token_invalid_password(auth_client, user):
    """POST /api/v1/auth/token/ com senha errada retorna 401."""
    response = auth_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "wrong"},
        content_type="application/json",
    )
    assert response.status_code == 401


def test_obtain_token_inactive_user(auth_client, inactive_planner):
    """POST /api/v1/auth/token/ com usuário inativo retorna 401."""
    response = auth_client.post(
        "/api/v1/auth/token/",
        {"email": inactive_planner.email, "password": "password123"},
        content_type="application/json",
    )
    assert response.status_code == 401


def test_refresh_token_success(auth_client, user):
    """POST /api/v1/auth/refresh/ com refresh válido retorna 200 com novos tokens."""
    obtain_resp = auth_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "password123"},
        content_type="application/json",
    )
    tokens = obtain_resp.json()

    response = auth_client.post(
        "/api/v1/auth/refresh/",
        {"refresh": tokens["refresh"]},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data
    # Com rotação ativa, o refresh deve ser diferente do original
    assert data["refresh"] != tokens["refresh"]


def test_refresh_token_reuse_after_rotation(auth_client, user):
    """Usar o mesmo refresh token duas vezes deve falhar na segunda (blacklist)."""
    obtain_resp = auth_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "password123"},
        content_type="application/json",
    )
    tokens = obtain_resp.json()

    # Primeiro uso: sucesso
    first = auth_client.post(
        "/api/v1/auth/refresh/",
        {"refresh": tokens["refresh"]},
        content_type="application/json",
    )
    assert first.status_code == 200

    # Segundo uso do MESMO refresh: deve falhar (token na blacklist)
    second = auth_client.post(
        "/api/v1/auth/refresh/",
        {"refresh": tokens["refresh"]},
        content_type="application/json",
    )
    assert second.status_code == 401


def test_verify_token_success(auth_client, user):
    """POST /api/v1/auth/verify/ com access token válido retorna 200."""
    obtain_resp = auth_client.post(
        "/api/v1/auth/token/",
        {"email": user.email, "password": "password123"},
        content_type="application/json",
    )
    tokens = obtain_resp.json()

    response = auth_client.post(
        "/api/v1/auth/verify/",
        {"token": tokens["access"]},
        content_type="application/json",
    )
    assert response.status_code == 200


def test_verify_token_invalid(auth_client):
    """POST /api/v1/auth/verify/ com token inválido retorna 401."""
    response = auth_client.post(
        "/api/v1/auth/verify/",
        {"token": "invalid.token.here"},
        content_type="application/json",
    )
    assert response.status_code == 401
