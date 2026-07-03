import pytest
from django.test import Client


@pytest.mark.django_db
def test_auth_token_throttling():
    client = Client()
    url = "/api/v1/auth/token/"
    payload = {"email": "throttled@example.com", "password": "password123"}

    # auth_anon rate is 10/minute.
    # Let's make 11 requests.
    for _ in range(10):
        response = client.post(url, payload, content_type="application/json")
        # Credentials don't exist, so we expect 401, not 429 yet
        assert response.status_code == 401

    # The 11th request should be throttled
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 429
    assert "Request was throttled" in response.json()["detail"]
