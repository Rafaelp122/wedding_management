"""Serviço de verificação de e-mail de usuários."""

from typing import cast

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.core.exceptions import ApplicationError
from apps.users.models import User


class EmailVerificationService:
    """
    Serviço de geração de tokens e envio de e-mails para verificação de contas.
    """

    @classmethod
    def send_verification_email(
        cls, user: User, frontend_url: str | None = None
    ) -> None:
        """Gera token seguro e envia e-mail transacional de confirmação para o usuário.

        Decisão Arquitetural: [Users Domain](docs/architecture/domains/users-domain.md)
        Efeitos Colaterais: Envia mensagem de e-mail via EmailMultiAlternatives.
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
        """Valida o token de verificação e ativa o cadastro do usuário.

        Decisão Arquitetural: [Users Domain](docs/architecture/domains/users-domain.md)
        Efeitos Colaterais: Atualiza is_email_verified, email_verified_at e is_active no banco.

        Raises:
            ApplicationError: Se o token for inválido, expirado ou usuário inexistente.
        """
        try:
            uid_decoded = urlsafe_base64_decode(uid).decode()
            user = User.objects.filter(uuid=uid_decoded).first()
        except (ValueError, TypeError):
            user = None

        if not user or not default_token_generator.check_token(user, token):
            user_desc = f"usuário '{user.email}'" if user else f"uid '{uid}'"
            raise ApplicationError(
                f"Link de verificação de e-mail inválido ou expirado para {user_desc}.",
                code="invalid_token",
            )

        user.verify_email()
        user.activate()
        user.save(
            update_fields=[
                "is_email_verified",
                "email_verified_at",
                "is_active",
                "updated_at",
            ]
        )

        return user

    @classmethod
    def resend_verification_email(
        cls, email: str, frontend_url: str | None = None
    ) -> None:
        """Reenvia o e-mail de confirmação caso o usuário exista e não esteja verificado.

        Decisão Arquitetural: [Users Domain](docs/architecture/domains/users-domain.md)
        Efeitos Colaterais: Dispara o envio de novo e-mail transacional de verificação.
        """
        email = User.objects.normalize_email(email)
        user = User.objects.filter(email=email).first()

        if user and not user.is_email_verified:
            cls.send_verification_email(user, frontend_url)
