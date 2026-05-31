import pytest

from apps.users.models import User


@pytest.mark.django_db
class TestAuthAPI:
    """Testes de integração para a API de autenticação e registro."""

    def test_register_user_success(self, client):
        """Garante que o registro de usuário com senha válida tem sucesso."""
        payload = {
            "email": "novo_user@exemplo.com",
            "password": "valid_password_123",
            "first_name": "Novo",
            "last_name": "Usuario",
        }

        response = client.post(
            "/api/v1/auth/register/", data=payload, content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert "uuid" in data
        assert data["email"] == "novo_user@exemplo.com"
        assert User.objects.filter(email="novo_user@exemplo.com").exists()

    def test_register_user_short_password_fails(self, client):
        """Garante que a API rejeita registro com senha menor de 8 caracteres."""
        payload = {
            "email": "invalid_pwd@exemplo.com",
            "password": "short",
            "first_name": "Curto",
            "last_name": "Password",
        }

        response = client.post(
            "/api/v1/auth/register/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422
        # Ninja standard schema validation error structure contains "detail"
        data = response.json()
        assert "detail" in data
        assert any("password" in str(error.get("loc", [])) for error in data["detail"])
