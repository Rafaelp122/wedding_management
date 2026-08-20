from typing import cast

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.core.exceptions import ApplicationError
from apps.users.models import User
from apps.users.services.password_reset_service import PasswordResetService
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestPasswordResetService:
    def test_request_password_reset_success(self) -> None:
        user = cast(User, UserFactory(email="test@example.com"))
        PasswordResetService.request_password_reset(email="test@example.com")

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Redefinição de Senha - Sim, Aceito!"
        assert mail.outbox[0].to == [user.email]
        assert "reset-password?uid=" in mail.outbox[0].body

    def test_request_password_reset_non_existent_user(self) -> None:
        PasswordResetService.request_password_reset(email="notfound@example.com")
        assert len(mail.outbox) == 0

    def test_confirm_password_reset_success(self) -> None:
        user = cast(User, UserFactory(email="test2@example.com"))
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        PasswordResetService.confirm_password_reset(uid, token, "NewStrongPass123!")
        user.refresh_from_db()
        assert user.check_password("NewStrongPass123!")

    def test_confirm_password_reset_invalid_token(self) -> None:
        user = cast(User, UserFactory())
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))

        with pytest.raises(ApplicationError) as exc_info:
            PasswordResetService.confirm_password_reset(
                uid, "invalid-token", "NewStrongPass123!"
            )

        assert exc_info.value.code == "invalid_token"
        assert exc_info.value.status_code == 400

    def test_confirm_password_reset_invalid_uid(self) -> None:
        user = cast(User, UserFactory())
        token = default_token_generator.make_token(user)

        with pytest.raises(ApplicationError) as exc_info:
            PasswordResetService.confirm_password_reset(
                "invalid-uid", token, "NewStrongPass123!"
            )

        assert exc_info.value.code == "invalid_token"

    def test_confirm_password_reset_weak_password(self) -> None:
        user = cast(User, UserFactory(email="weak@example.com"))
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        with pytest.raises(ApplicationError) as exc_info:
            PasswordResetService.confirm_password_reset(uid, token, "12345678")

        assert exc_info.value.code == "invalid_password"
