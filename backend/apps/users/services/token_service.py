import logging

from django.contrib.auth import authenticate
from ninja.errors import HttpError
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.tokens import RefreshToken

from apps.users.schemas import TokenOut, UserDataOut, VerifyTokenOut


logger = logging.getLogger(__name__)


class TokenService:
    """
    Serviço de orquestração para autenticação e geração de tokens JWT.
    Centraliza a lógica de validação de credenciais, criação de tokens
    e montagem da resposta.
    """

    @staticmethod
    def obtain(email: str, password: str) -> TokenOut:
        """
        Autentica o usuário por email/senha e retorna tokens JWT.

        Raises:
            HttpError (401): Se as credenciais forem inválidas ou a conta
                estiver desativada.
        """
        logger.info("Tentativa de obtenção de token para email=%s", email)

        user = authenticate(request=None, username=email, password=password)

        if user is None:
            logger.warning("Falha de autenticação para email=%s", email)
            raise HttpError(401, "Credenciais inválidas ou conta desativada.")

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

        logger.info("Token gerado com sucesso para user uuid=%s", user.uuid)
        return token_out

    @staticmethod
    def refresh(refresh_token: str) -> TokenRefreshOutputSchema:
        """
        Gera um novo par de tokens a partir de um refresh token válido.

        Se ROTATE_REFRESH_TOKENS estiver ativo (padrão), o refresh token
        anterior é invalidado (blacklist) e um novo refresh é emitido.

        Raises:
            HttpError (401): Se o refresh token for inválido ou estiver
                na blacklist.
        """
        logger.info("Tentativa de refresh de token")
        schema = TokenRefreshInputSchema(refresh=refresh_token)
        result = schema.to_response_schema()
        logger.info("Token refresh bem-sucedido")
        return result

    @staticmethod
    def verify(token: str) -> VerifyTokenOut:
        """
        Verifica se um token JWT é válido e não expirou.

        Raises:
            HttpError (401): Se o token for inválido ou expirado.
        """
        logger.info("Tentativa de verificação de token")
        schema = TokenVerifyInputSchema(token=token)
        schema.to_response_schema()  # levanta HttpError(401) se inválido
        logger.info("Token verificado com sucesso")
        return VerifyTokenOut()
