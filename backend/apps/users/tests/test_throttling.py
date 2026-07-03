import pytest


@pytest.mark.django_db
class TestThrottling:
    """
    Testes para garantir que o rate limiting (throttling) está funcionando.
    """

    def test_register_throttling(self, client):
        """
        Garante que após 5 requisições de registro, a 6ª retorna 429.
        """
        payload = {
            "email": "throttle-test@example.com",
            "password": "valid_password_123",
            "first_name": "Throttle",
            "last_name": "Test",
            "company_name": "Test Co",
        }

        # Realiza 5 requisições (limite configurado como 5/m)
        for i in range(5):
            response = client.post(
                "/api/v1/auth/register/",
                data={**payload, "email": f"user{i}@example.com"},
                content_type="application/json",
            )
            assert response.status_code == 201

        # A 6ª requisição deve falhar com 429
        response = client.post(
            "/api/v1/auth/register/",
            data={**payload, "email": "user6@example.com"},
            content_type="application/json",
        )
        assert response.status_code == 429
        data = response.json()
        assert "detail" in data
        assert "Request was throttled" in data["detail"]

    def test_obtain_token_throttling(self, client, user_factory):
        """
        Garante que após 5 requisições de login, a 6ª retorna 429.
        """
        user_factory.create(email="login-throttle@example.com", password="password123")
        payload = {
            "email": "login-throttle@example.com",
            "password": "password123",
        }

        # Realiza 5 requisições
        for _ in range(5):
            response = client.post(
                "/api/v1/auth/token/", data=payload, content_type="application/json"
            )
            assert response.status_code == 200

        # A 6ª requisição deve falhar com 429
        response = client.post(
            "/api/v1/auth/token/", data=payload, content_type="application/json"
        )
        assert response.status_code == 429
        data = response.json()
        assert "detail" in data
        assert "Request was throttled" in data["detail"]
