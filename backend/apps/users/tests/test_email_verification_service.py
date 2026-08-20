from typing import Any

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from apps.core.exceptions import ApplicationError
from apps.users.services.email_verification_service import EmailVerificationService


@pytest.mark.django_db
class TestEmailVerificationService:
    def test_send_verification_email(self, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        EmailVerificationService.send_verification_email(user)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Confirme seu e-mail"
        assert user.email in mail.outbox[0].to

    def test_verify_email_success(self, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        verified_user = EmailVerificationService.verify_email(uid, token)

        assert verified_user.is_email_verified is True
        assert verified_user.is_active is True
        assert verified_user.email_verified_at is not None

    def test_verify_email_invalid_token(self, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        uid = urlsafe_base64_encode(force_bytes(str(user.uuid)))

        with pytest.raises(ApplicationError) as exc_info:
            EmailVerificationService.verify_email(uid, "invalid-token")

        assert exc_info.value.code == "invalid_token"

    def test_resend_verification_email_success(self, user_factory: Any) -> None:
        user = user_factory.create(is_active=False, is_email_verified=False)
        EmailVerificationService.resend_verification_email(user.email)

        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == "Confirme seu e-mail"

    def test_resend_verification_email_already_verified(
        self, user_factory: Any
    ) -> None:
        user = user_factory.create(is_active=True, is_email_verified=True)
        EmailVerificationService.resend_verification_email(user.email)

        assert len(mail.outbox) == 0

    def test_resend_verification_email_non_existent(self, user_factory: Any) -> None:
        EmailVerificationService.resend_verification_email("nonexistent@example.com")

        assert len(mail.outbox) == 0
