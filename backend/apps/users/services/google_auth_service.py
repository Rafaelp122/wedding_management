import logging
from typing import Any

from django.conf import settings
from django.db import transaction
from google.auth.transport import requests
from google.oauth2 import id_token as google_id_token
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from apps.tenants.services.tenant_service import TenantService
from apps.users.models import User
from apps.users.schemas import TokenOut, UserDataOut


logger = logging.getLogger(__name__)


class GoogleAuthService:
    """
    Serviço de autenticação e provisionamento via Google OAuth2.

    Centraliza a verificação de tokens de identidade do Google, criação de novos
    usuários com seus respectivos tenants isolados e emissão de tokens JWT.
    """

    @staticmethod
    @transaction.atomic
    def authenticate_with_google(id_token: str) -> TokenOut:
        """
        Autentica usuário existente ou cadastra um novo via ID Token do Google.

        Args:
            id_token: O token JWT de identidade emitido pelo Google OAuth.

        Returns:
            TokenOut contendo os tokens de acesso, atualização e os dados do usuário.

        Raises:
            HttpError: Se o token do Google for inválido ou expirado (HTTP 401),
                ou se a conta do usuário estiver inativa (HTTP 401).
        """
        logger.info("Iniciando verificação de token de identidade do Google.")

        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "") or None

        try:
            id_info: dict[str, Any] = google_id_token.verify_oauth2_token(
                id_token,
                requests.Request(),
                audience=client_id,
            )
        except ValueError as e:
            logger.warning(f"Falha ao validar token do Google: {e}")
            raise HttpError(401, "Token do Google inválido ou expirado.") from e

        email = id_info.get("email")
        if not email:
            logger.warning("Token do Google validado não contém o campo de e-mail.")
            raise HttpError(401, "Token do Google inválido ou expirado.")

        first_name = id_info.get("given_name", "")
        last_name = id_info.get("family_name", "")

        user = User.objects.filter(email=email).first()

        if user:
            if not user.is_active:
                logger.warning(
                    f"Tentativa de login via Google para conta inativa: {email}"
                )
                raise HttpError(401, "Credenciais inválidas ou conta desativada.")
        else:
            logger.info(f"Provisionando novo usuário via Google OAuth: {email}")
            random_password = User.objects.make_random_password()
            display_name = f"{first_name} {last_name}".strip() or email
            company = TenantService.create_company(display_name)

            user = User.objects.create_user(
                email=email,
                password=random_password,
                company=company,
                first_name=first_name,
                last_name=last_name,
                is_active=True,
            )

        refresh = RefreshToken.for_user(user)
        token_out = TokenOut(
            access=str(refresh.access_token),  # type: ignore[attr-defined]
            refresh=str(refresh),
            user=UserDataOut(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ),
        )

        logger.info(f"Autenticação via Google concluída para o usuário: {email}")
        return token_out
