import pytest
from django.core.cache import cache


@pytest.mark.django_db
def test_obtain_token_rate_limiting(client, user):
    """
    Testa se o endpoint de obtenção de token respeita o limite de 5 requisições
    por minuto.
    """
    cache.clear()
    url = "/api/v1/auth/token/"
    payload = {
        "email": user.email,
        "password": "password123",
    }

    # As primeiras 5 requisições devem passar (ou pelo menos não retornar 429)
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        assert response.status_code != 429

    # A 6ª requisição deve ser bloqueada com 429 Too Many Requests
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
    data = response.json()
    assert "detail" in data
    assert "throttled" in str(data["detail"]).lower()


@pytest.mark.django_db
def test_register_user_rate_limiting(client):
    """
    Testa se o endpoint de registro respeita o limite de 5 requisições por minuto.
    """
    cache.clear()
    url = "/api/v1/auth/register/"
    payload = {
        "email": "limiter@example.com",
        "password": "password123",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test Co",
    }

    for i in range(5):
        # Mudar o email para não falhar na validação de unicidade antes do throttle
        current_payload = payload.copy()
        current_payload["email"] = f"limiter-{i}@example.com"
        response = client.post(url, current_payload, content_type="application/json")
        assert response.status_code != 429

    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
