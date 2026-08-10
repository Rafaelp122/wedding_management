import logging

import django.contrib.auth.password_validation as password_validation
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.core.exceptions import ApplicationError


User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetService:
    @staticmethod
    def request_password_reset(email: str, frontend_url: str | None = None) -> None:
        """
        Inicia o fluxo de redefinição de senha para o e-mail fornecido.
        """
        email_normalized = email.strip().lower()
        user = User.objects.filter(
            email__iexact=email_normalized, is_active=True
        ).first()

        if not user:
            logger.warning(
                "Tentativa de redefinição de senha para e-mail "
                f"inexistente ou inativo: {email_normalized}"
            )
            return

        uidb64 = urlsafe_base64_encode(force_bytes(str(user.uuid)))
        token = default_token_generator.make_token(user)

        base_url = frontend_url or getattr(
            settings, "FRONTEND_URL", "http://localhost:5173"
        )
        reset_url = f"{base_url}/reset-password?uid={uidb64}&token={token}"

        context = {
            "user": user,
            "reset_url": reset_url,
        }

        subject = "Redefinição de Senha - Sim, Aceito!"
        text_content = render_to_string("emails/password_reset.txt", context)
        html_content = render_to_string("emails/password_reset.html", context)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    @staticmethod
    def confirm_password_reset(uid: str, token: str, new_password: str) -> None:
        """
        Confirma a redefinição de senha validando o uid e o token.
        """
        try:
            uid_decoded = urlsafe_base64_decode(uid).decode("utf-8")
            user = User.objects.get(uuid=uid_decoded)
        except (ValueError, TypeError, User.DoesNotExist, UnicodeDecodeError) as err:
            raise ApplicationError(
                detail="Link de redefinição de senha inválido ou expirado.",
                code="invalid_token",
            ) from err

        if not default_token_generator.check_token(user, token):
            raise ApplicationError(
                detail="Link de redefinição de senha inválido ou expirado.",
                code="invalid_token",
            )

        try:
            password_validation.validate_password(new_password, user=user)
        except DjangoValidationError as e:
            raise ApplicationError(
                detail=e.messages[0],
                code="invalid_password",
            ) from e

        user.set_password(new_password)
        user.save()
