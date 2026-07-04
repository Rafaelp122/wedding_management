import pytest
from django.core.cache import cache


@pytest.mark.django_db
def test_token_endpoint_throttling(client):
    """
    Verifica se o endpoint de obtenção de token aplica o limite de taxa (throttling).
    O limite configurado é 5/m para anônimos.
    """
    # Limpa o cache para garantir isolamento do teste
    cache.clear()

    url = "/api/v1/auth/token/"
    payload = {
        "email": "throttled@example.com",
        "password": "wrong-password",
    }

    # Faz 5 requisições (dentro do limite)
    for _ in range(5):
        response = client.post(
            url,
            payload,
            content_type="application/json",
        )
        # O status pode ser 401 (senha errada) ou outro, mas não deve ser 429 ainda.
        assert response.status_code != 429

    # A 6ª requisição deve ser bloqueada (429 Too Many Requests)
    response = client.post(
        url,
        payload,
        content_type="application/json",
    )
    assert response.status_code == 429
    data = response.json()
    assert "detail" in data
    detail = data["detail"].lower()
    assert (
        "request was throttled" in detail
        or "limite de requisições" in detail
        or "throttled" in detail
    )
