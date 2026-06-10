import hashlib
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
        logger.info(f"Tentativa de obtenção de token para email={email}")

        user = authenticate(request=None, username=email, password=password)

        if user is None:
            logger.warning(f"Falha de autenticação para email={email}")
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

        logger.info(f"Token gerado com sucesso para user uuid={user.uuid}")
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
        token_fp = hashlib.sha256(refresh_token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de refresh de token (fp={token_fp})")
        schema = TokenRefreshInputSchema(refresh=refresh_token)
        result = schema.to_response_schema()
        logger.info(f"Token refresh bem-sucedido (fp={token_fp})")
        return result

    @staticmethod
    def verify(token: str) -> VerifyTokenOut:
        """
        Verifica se um token JWT é válido e não expirou.

        Raises:
            HttpError (401): Se o token for inválido ou expirado.
        """
        token_fp = hashlib.sha256(token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de verificação de token (fp={token_fp})")
        schema = TokenVerifyInputSchema(token=token)
        schema.to_response_schema()  # levanta HttpError(401) se inválido
        logger.info(f"Token verificado com sucesso (fp={token_fp})")
        return VerifyTokenOut()
