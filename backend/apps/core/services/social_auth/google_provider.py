import logging
from typing import Any

from django.conf import settings
from google.auth.transport import requests
from google.oauth2 import id_token as google_id_token
from ninja.errors import HttpError

from .base import OAuthUserInfo


logger = logging.getLogger(__name__)


class GoogleOAuthProvider:
    """
    Provedor de autenticação OAuth2 do Google.

    Verifica tokens de identidade do Google e extrai os dados do usuário.
    """

    def verify_token(self, token: str) -> OAuthUserInfo:
        """
        Verifica o token do Google e extrai as informações do usuário.

        Args:
            token: O token JWT de identidade emitido pelo Google.

        Returns:
            OAuthUserInfo contendo os dados do usuário.

        Raises:
            HttpError: Se a configuração estiver ausente (401), token for
                inválido/expirado (401), ou e-mail não for verificado (401).
        """
        client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
        if not client_id:
            logger.warning("Configuração GOOGLE_CLIENT_ID ausente no servidor.")
            raise HttpError(401, "Configuração do Google OAuth ausente no servidor.")

        try:
            id_info: dict[str, Any] = google_id_token.verify_oauth2_token(
                token,
                requests.Request(),
                client_id,
            )
        except Exception as e:
            logger.warning(f"Falha ao validar token do Google: {e}")
            raise HttpError(401, "Token do Google inválido ou expirado.") from e

        email_verified = id_info.get("email_verified")
        if email_verified is not True:
            logger.warning("Tentativa de login com e-mail do Google não verificado.")
            raise HttpError(401, "E-mail do Google não verificado.")

        email = id_info.get("email")
        if not email:
            logger.warning("Token do Google válido mas sem campo e-mail.")
            raise HttpError(401, "E-mail não fornecido pelo Google.")

        first_name = id_info.get("given_name", "")[:150]
        last_name = id_info.get("family_name", "")[:150]
        sub = id_info.get("sub", "")

        return OAuthUserInfo(
            email=email,
            email_verified=True,
            first_name=first_name,
            last_name=last_name,
            sub=sub,
        )
