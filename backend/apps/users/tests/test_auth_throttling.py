import pytest


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url,payload",
    [
        (
            "/api/v1/auth/token/",
            {"email": "throttled@example.com", "password": "password123"},
        ),
        (
            "/api/v1/auth/register/",
            {
                "email": "throttled@example.com",
                "password": "Password123!",
                "first_name": "Throttle",
                "last_name": "Test",
                "company_name": "Throttle Co",
            },
        ),
        ("/api/v1/auth/refresh/", {"refresh": "invalid-token-value"}),
        ("/api/v1/auth/verify/", {"token": "invalid-token-value"}),
    ],
)
def test_auth_endpoint_exceeds_rate_limit_returns_429(client, url, payload):
    """
    Garante que os endpoints de autenticação retornam 429
    após exceder o limite de 5 req/min.
    """
    for _ in range(5):
        response = client.post(url, payload, content_type="application/json")
        assert response.status_code != 429

    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
    assert "detail" in response.json()
    assert "Request was throttled" in response.json()["detail"]


@pytest.mark.django_db
def test_auth_throttling_scopes_are_isolated_and_independent(client):
    """
    Garante que requisições em um endpoint de autenticação
    não interferem no limite do outro.
    """
    token_url = "/api/v1/auth/token/"
    token_payload = {"email": "throttled@example.com", "password": "password123"}

    register_url = "/api/v1/auth/register/"
    register_payload = {
        "email": "throttled@example.com",
        "password": "Password123!",
        "first_name": "Throttle",
        "last_name": "Test",
        "company_name": "Throttle Co",
    }

    # Esgota o limite do endpoint de token (5 requisições)
    for _ in range(5):
        response = client.post(
            token_url, token_payload, content_type="application/json"
        )
        assert response.status_code != 429

    # O 6º request para token é bloqueado
    assert (
        client.post(
            token_url, token_payload, content_type="application/json"
        ).status_code
        == 429
    )

    # Mas o endpoint de register (que possui escopo isolado)
    # ainda aceita requisições normalmente
    response = client.post(
        register_url, register_payload, content_type="application/json"
    )
    assert response.status_code != 429
