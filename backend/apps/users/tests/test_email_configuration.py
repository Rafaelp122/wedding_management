from typing import cast

import pytest
from django.core import mail
from django.test import override_settings

from apps.users.models import User
from apps.users.services.email_verification_service import EmailVerificationService
from apps.users.services.password_reset_service import PasswordResetService
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestEmailConfiguration:
    """Testes para garantir o uso correto de configurações de e-mail transacional."""

    @override_settings(DEFAULT_FROM_EMAIL="contato@simaceito.site")
    def test_email_verification_uses_custom_default_from_email(self) -> None:
        user = cast(User, UserFactory(is_active=False, is_email_verified=False))
        EmailVerificationService.send_verification_email(user)

        assert len(mail.outbox) == 1
        sent_email = mail.outbox[0]
        assert sent_email.from_email == "contato@simaceito.site"
        assert user.email in sent_email.to
        assert "Confirme seu e-mail" in sent_email.subject

    @override_settings(DEFAULT_FROM_EMAIL="contato@simaceito.site")
    def test_password_reset_uses_custom_default_from_email(self) -> None:
        user = cast(User, UserFactory(email="recuperar@simaceito.site"))
        PasswordResetService.request_password_reset(email=user.email)

        assert len(mail.outbox) == 1
        sent_email = mail.outbox[0]
        assert sent_email.from_email == "contato@simaceito.site"
        assert sent_email.to == [user.email]
        assert "Redefinição de Senha - Sim, Aceito!" in sent_email.subject
