from typing import Any

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


@pytest.mark.django_db
class TestEmailVerificationAPI:
    def test_verify_email_success(self, client: Any, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        response = client.post(
            "/api/v1/auth/verify-email/",
            data={"uid": uid, "token": token},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["message"] == "E-mail verificado com sucesso."

        user.refresh_from_db()
        assert user.is_email_verified is True
        assert user.is_active is True

    def test_verify_email_invalid_token(self, client: Any, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))

        response = client.post(
            "/api/v1/auth/verify-email/",
            data={"uid": uid, "token": "invalid-token"},
            content_type="application/json",
        )

        assert response.status_code == 400
        assert response.json()["code"] == "invalid_token"

    def test_resend_verification_email(self, client: Any, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)

        response = client.post(
            "/api/v1/auth/resend-verification/",
            data={"email": user.email},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert (
            response.json()["message"]
            == "Se a conta existir e não estiver verificada, "
            "o e-mail será reenviado."
        )
