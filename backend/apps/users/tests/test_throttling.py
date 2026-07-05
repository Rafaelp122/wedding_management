import pytest


@pytest.mark.django_db
def test_register_throttling(auth_client):
    """
    Verify that the rate limit (5 requests per minute for anonymous users) is enforced.
    """
    payload = {
        "email": "throttle@test.com",
        "password": "StrongPassword123!",
        "first_name": "Throttle",
        "last_name": "Test",
        "company_name": "Throttle Co",
    }

    # The first 5 requests should pass (status code 201)
    for i in range(5):
        payload["email"] = f"throttle_{i}@test.com"
        response = auth_client.post(
            "/api/v1/auth/register/",
            payload,
            content_type="application/json",
        )
        assert response.status_code == 201

    # The 6th request should return 429
    payload["email"] = "throttle_6@test.com"
    response = auth_client.post(
        "/api/v1/auth/register/",
        payload,
        content_type="application/json",
    )

    assert response.status_code == 429
    assert "Request was throttled" in response.json()["detail"]
