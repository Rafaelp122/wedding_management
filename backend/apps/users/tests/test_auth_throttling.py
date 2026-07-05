import pytest


@pytest.mark.django_db
def test_obtain_token_throttling(client):
    """
    Verifica se o endpoint /token/ aplica rate limiting.
    (5 requisições por minuto para anônimos).
    """
    url = "/api/v1/auth/token/"
    payload = {"email": "throttled@example.com", "password": "somepassword123"}

    # Faz 5 requisições (limite configurado: 5/m)
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        # Pode ser 401 ou 200, não importa aqui, o que importa é que NÃO seja 429 ainda.
        assert response.status_code != 429

    # A 6ª requisição deve falhar com 429
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429

    data = response.json()
    assert "detail" in data
    # Ninja Extra padrão retorna "Request was throttled."
    assert "throttled" in data["detail"].lower()


@pytest.mark.django_db
def test_register_throttling(client):
    """
    Verifica se o endpoint /register/ aplica rate limiting.
    """
    url = "/api/v1/auth/register/"
    payload = {
        "email": "newuser@example.com",
        "password": "password123",
        "first_name": "John",
        "last_name": "Doe",
        "company_name": "Doe Corp",
    }

    # Faz 5 requisições
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        assert response.status_code != 429

    # A 6ª requisição deve falhar com 429
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
