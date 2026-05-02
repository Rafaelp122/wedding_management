import pytest
from ninja_jwt.tokens import RefreshToken


@pytest.mark.django_db
def test_jwt_bearer_manual(client, user):
    """Pass the header directly to confirm HttpBearer picks it up."""
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    # Also test what the API returns for clues
    response = client.get(
        "/api/v1/weddings/",
        HTTP_AUTHORIZATION=f"Bearer {token}",
    )
    body = response.json()
    print(f"\nstatus: {response.status_code}")
    print(f"body: {body}")

    # Also check without 'Bearer' to see if it says anything different
    r2 = client.get(
        "/api/v1/weddings/",
        HTTP_AUTHORIZATION=f"Token {token}",
    )
    print(f"r2 status (Token prefix): {r2.status_code}, body: {r2.json()}")
    assert response.status_code == 200
