import pytest
from django.contrib.auth import get_user_model

from apps.tenants.models import Company


User = get_user_model()


@pytest.mark.django_db
@pytest.mark.api
class TestAuthAPI:
    def test_register_user_success_and_creates_company(self, client):
        """RF-SEC: Cadastro cria usuário e Tenant Silencioso."""
        payload = {
            "email": "novo_user@test.com",
            "password": "password123",
            "first_name": "Novo",
            "last_name": "Usuário",
        }

        response = client.post(
            "/api/v1/auth/register/", data=payload, content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert "access" in data
        assert data["user"]["email"] == "novo_user@test.com"

        # Verifica se o Tenant Silencioso funcionou
        user = User.objects.get(email="novo_user@test.com")
        assert user.company is not None
        assert isinstance(user.company, Company)
        assert "Agência de Novo Usuário" in user.company.name

    def test_register_duplicate_email_fails(self, client, user):
        """Validação: Não permite dois usuários com mesmo email."""
        payload = {
            "email": user.email,
            "password": "password123",
            "first_name": "Outro",
            "last_name": "User",
        }

        response = client.post(
            "/api/v1/auth/register/", data=payload, content_type="application/json"
        )

        assert response.status_code == 400
        assert "já está cadastrado" in response.json()["detail"]

    def test_login_success(self, client, user):
        """Garante que o login customizado retorna dados do usuário."""
        payload = {
            "email": user.email,
            "password": "password123",  # Assumindo a senha padrão da factory
        }

        # Primeiro garantimos que o user tem a senha password123
        user.set_password("password123")
        user.save()

        response = client.post(
            "/api/v1/auth/token/", data=payload, content_type="application/json"
        )

        assert response.status_code == 200
        data = response.json()
        assert "access" in data
        assert data["user"]["id"] == user.id
