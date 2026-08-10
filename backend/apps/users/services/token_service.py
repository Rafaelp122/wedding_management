import hashlib
import logging

from django.contrib.auth import authenticate
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.tokens import RefreshToken

from apps.core.exceptions import AuthenticationFailedError
from apps.users.schemas import TokenOut, UserDataOut, VerifyTokenOut


logger = logging.getLogger(__name__)


class TokenService:
    """
    Serviço de orquestração para autenticação e geração de tokens JWT.

    Centraliza a lógica de validação de credenciais, criação de tokens
    e montagem da resposta com dados do usuário autenticado.
    """

    @staticmethod
    def obtain(email: str, password: str) -> TokenOut:
        """
        Autentica o usuário por e-mail e senha, gerando os tokens JWT correspondentes.

        Args:
            email: O endereço de e-mail do usuário para autenticação.
            password: A senha em texto puro fornecida pelo usuário.

        Returns:
            TokenOut contendo o token de acesso (access), o token de atualização
            (refresh) e os dados básicos do usuário autenticado.

        Raises:
            AuthenticationFailedError: Caso as credenciais sejam inválidas ou a conta
                esteja inativa.
        """
        logger.info(f"Tentativa de obtenção de token para email={email}")

        user = authenticate(request=None, username=email, password=password)

        if user is None:
            from apps.users.models import User

            potential_user = User.objects.filter(email=email).first()
            if potential_user and potential_user.check_password(password):
                if not potential_user.is_email_verified:
                    raise AuthenticationFailedError(
                        "Sua conta ainda não foi ativada. "
                        "Verifique sua caixa de entrada para confirmar seu e-mail.",
                        code="email_not_verified",
                    )

            logger.warning(f"Falha de autenticação para email={email}")
            raise AuthenticationFailedError(
                "Credenciais inválidas ou conta desativada.",
                code="invalid_credentials",
            )

        # ninja_jwt v5.4.5 alterou a assinatura de for_user
        refresh = RefreshToken.for_user(user)  # type: ignore[misc]
        token_out = TokenOut(
            access=str(refresh.access_token),
            refresh=str(refresh),
            user=UserDataOut(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_email_verified=user.is_email_verified,
            ),
        )

        logger.info(f"Token gerado com sucesso para user uuid={user.uuid}")
        return token_out

    @staticmethod
    def refresh(refresh_token: str) -> TokenRefreshOutputSchema:
        """
        Gera um novo par de tokens a partir de um token de atualização (refresh token).

        Se a rotação de tokens estiver ativa (padrão do ninja_jwt), o token antigo
        será invalidado e adicionado à blacklist, emitindo-se um novo refresh.

        Args:
            refresh_token: O refresh token atual recebido na requisição.

        Returns:
            TokenRefreshOutputSchema contendo o novo token de acesso e,
            opcionalmente, o novo refresh token.

        Raises:
            HttpError: Se o refresh token for inválido, estiver expirado ou
                constar na blacklist.
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
        Verifica a integridade e a validade temporal de um token JWT.

        Args:
            token: O token JWT (geralmente o access token) a ser validado.

        Returns:
            VerifyTokenOut indicando sucesso caso o token seja válido.

        Raises:
            HttpError: Se o token for inválido, estiver corrompido ou expirado.
        """
        token_fp = hashlib.sha256(token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de verificação de token (fp={token_fp})")
        schema = TokenVerifyInputSchema(token=token)
        # O método levanta HttpError(401) caso o token seja inválido.
        schema.to_response_schema()
        logger.info(f"Token verificado com sucesso (fp={token_fp})")
        return VerifyTokenOut()
