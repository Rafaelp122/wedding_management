from typing import Any, cast

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import Client
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


@pytest.fixture
def unauth_client() -> Client:
    return Client()


@pytest.mark.django_db
class TestPasswordResetAPI:
    def test_request_password_reset(self, unauth_client: Client) -> None:
        UserFactory(email="test_api@example.com")

        response = unauth_client.post(
            "/api/v1/auth/password-reset/request/",
            {"email": "test_api@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert (
            response.json()["message"]
            == "Se o e-mail existir, você receberá as instruções em breve."
        )
        assert len(mail.outbox) == 1

    def test_request_password_reset_non_existent_user(
        self, unauth_client: Client
    ) -> None:
        response = unauth_client.post(
            "/api/v1/auth/password-reset/request/",
            {"email": "notfound@example.com"},
            content_type="application/json",
        )

        assert response.status_code == 200
        assert (
            response.json()["message"]
            == "Se o e-mail existir, você receberá as instruções em breve."
        )
        assert len(mail.outbox) == 0

    def test_confirm_password_reset(self, unauth_client: Client) -> None:

        user = UserFactory()
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        payload = {"uid": uid, "token": token, "new_password": "NewStrongPass123!"}

        response = unauth_client.post(
            "/api/v1/auth/password-reset/confirm/",
            payload,
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Senha redefinida com sucesso."

        user.refresh_from_db()
        assert user.check_password("NewStrongPass123!")

    def test_confirm_password_reset_invalid(self, unauth_client: Client) -> None:
        payload = {
            "uid": "invalid",
            "token": "invalid",
            "new_password": "NewStrongPass123!",
        }

        response = unauth_client.post(
            "/api/v1/auth/password-reset/confirm/",
            payload,
            content_type="application/json",
        )
        assert response.status_code == 400
        assert response.json()["code"] == "invalid_token"
