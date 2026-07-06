import pytest
from django.core.cache import cache

@pytest.mark.django_db
def test_token_endpoint_throttling(client):
    """
    Test that the /auth/token/ endpoint is throttled after 5 requests.
    """
    # Clear cache to ensure a clean start
    cache.clear()

    url = "/api/v1/auth/token/"
    payload = {
        "email": "throttling-test@example.com",
        "password": "somepassword123"
    }

    # Send 5 requests (within the limit)
    for _ in range(5):
        response = client.post(
            url,
            payload,
            content_type="application/json"
        )
        # We don't care about 200/401 here, just that it's NOT 429
        assert response.status_code != 429

    # The 6th request should be throttled
    response = client.post(
        url,
        payload,
        content_type="application/json"
    )

    assert response.status_code == 429
    assert "Request was throttled" in response.json()["detail"]
