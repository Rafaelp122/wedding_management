import logging
from typing import Any, cast

from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from apps.users.schemas import TokenOut, UserDataOut


logger = logging.getLogger(__name__)


class TokenService:
    """
    Serviço de orquestração para autenticação e geração de tokens JWT.
    Centraliza a lógica de validação de credenciais, criação de tokens
    e montagem da resposta.
    """

    @staticmethod
    def obtain(email: str, password: str, request: HttpRequest) -> TokenOut:
        """
        Autentica o usuário por email/senha e retorna tokens JWT.

        Raises:
            HttpError (401): Se as credenciais forem inválidas ou a conta
                estiver desativada.
        """
        logger.info("Tentativa de obtenção de token para email=%s", email)

        user = authenticate(request, username=email, password=password)

        if user is None:
            logger.warning("Falha de autenticação para email=%s", email)
            raise HttpError(401, "Credenciais inválidas ou conta desativada.")

        refresh = cast(Any, RefreshToken.for_user(user))

        token_out = TokenOut(
            access=str(refresh.access_token),
            refresh=str(refresh),
            user=UserDataOut(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ),
        )

        logger.info("Token gerado com sucesso para user uuid=%s", user.uuid)
        return token_out
