"""Serviço de verificação de e-mail de usuários."""

from typing import cast

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.core.exceptions import ApplicationError
from apps.users.models import User


class EmailVerificationService:
    """Serviço responsável por gerar tokens e enviar e-mails de verificação."""

    @classmethod
    def send_verification_email(
        cls, user: User, frontend_url: str | None = None
    ) -> None:
        """Gera o token e envia o e-mail de verificação para o usuário.

        Args:
            user (User): Usuário que receberá o e-mail.
            frontend_url (str | None): URL base do frontend. Se None, usará do settings.
        """
        uidb64 = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        base_url = frontend_url or cast(
            str, getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        )
        verify_url = f"{base_url.rstrip('/')}/verify-email?uid={uidb64}&token={token}"

        context = {
            "user": user,
            "verify_url": verify_url,
        }

        subject = "Confirme seu e-mail"
        text_content = render_to_string("emails/email_verification.txt", context)
        html_content = render_to_string("emails/email_verification.html", context)

        email_message = EmailMultiAlternatives(
            subject,
            text_content,
            getattr(settings, "DEFAULT_FROM_EMAIL", "webmaster@localhost"),
            [user.email],
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

    @classmethod
    def verify_email(cls, uid: str, token: str) -> User:
        """Verifica o token de e-mail e ativa o usuário.

        Args:
            uid (str): UID codificado em base64 do usuário.
            token (str): Token gerado pelo default_token_generator.

        Returns:
            User: O usuário verificado.

        Raises:
            ApplicationError: Se o uid, token forem inválidos ou expirados.
        """
        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.filter(uuid=uid_decoded).first()
        except (ValueError, TypeError):
            user = None

        if not user or not default_token_generator.check_token(user, token):
            raise ApplicationError(
                "Link de verificação de e-mail inválido ou expirado.",
                code="invalid_token",
            )

        user.is_email_verified = True
        user.is_active = True
        user.email_verified_at = timezone.now()
        user.save()

        return user

    @classmethod
    def resend_verification_email(
        cls, email: str, frontend_url: str | None = None
    ) -> None:
        """Reenvia o e-mail de verificação.

        Apenas reenvia se o usuário existir e não estiver verificado.


        Args:
            email (str): E-mail do usuário.
            frontend_url (str | None): URL base do frontend.
        """
        email = User.objects.normalize_email(email)
        user = User.objects.filter(email=email).first()

        if user and not user.is_email_verified:
            cls.send_verification_email(user, frontend_url)
