import pytest


@pytest.mark.django_db
def test_obtain_token_throttling(client):
    """
    Verifica se o endpoint /auth/token/ possui rate limiting (throttling).
    A taxa configurada para 'anon' é 5/m.
    """
    url = "/api/v1/auth/token/"
    payload = {
        "email": "throttled@example.com",
        "password": "wrong-password"
    }

    # Executa 5 requisições (dentro do limite)
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        # Pode ser 401 ou 422 dependendo do payload, mas não deve ser 429
        assert response.status_code != 429

    # A 6ª requisição deve ser bloqueada com 429 Too Many Requests
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
    data = response.json()
    assert "detail" in data
    assert "Request was throttled" in data["detail"]

@pytest.mark.django_db
def test_register_throttling(client):
    """
    Verifica se o endpoint /auth/register/ possui rate limiting (throttling).
    """
    url = "/api/v1/auth/register/"
    payload = {
        "email": "register-throttled@example.com",
        "password": "password123",
        "first_name": "Throttled",
        "last_name": "User",
        "company_name": "Spam Inc"
    }

    # Executa 5 requisições
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        assert response.status_code != 429

    # A 6ª requisição deve ser bloqueada
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
