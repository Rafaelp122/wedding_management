import hashlib
import logging
from typing import cast

from django.contrib.auth import authenticate
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.tokens import RefreshToken

from apps.core.exceptions import AccountLockedError, AuthenticationFailedError
from apps.core.logging import mask_email
from apps.users.schemas import TokenOut, UserDataOut, VerifyTokenOut
from apps.users.services.lockout_service import LockoutService


logger = logging.getLogger(__name__)


class TokenService:
    """
    Serviço de orquestração para autenticação e geração de tokens JWT.

    Centraliza a lógica de validação de credenciais, criação de tokens
    e montagem da resposta com dados do usuário autenticado.

    Regra de Negócio:
        BR-U02 (docs/architecture/domains/users-domain.md)
    """

    @staticmethod
    def obtain(email: str, password: str) -> TokenOut:
        """Autentica o usuário por e-mail e senha, gerando os tokens JWT correspondentes.

        Regra de Negócio: [BR-U02](docs/architecture/domains/users-domain.md)
        Efeitos Colaterais: Registra falhas no cache ou limpa contadores após sucesso.

        Raises:
            AuthenticationFailedError: Se as credenciais forem inválidas, conta inativa ou e-mail não verificado.
            AccountLockedError: Se a conta estiver temporariamente bloqueada por excesso de falhas.
        """
        masked = mask_email(email)
        logger.info(f"Tentativa de obtenção de token para email={masked}")

        # 1. Verifica se a conta está sob bloqueio temporário (Account Lockout)
        if LockoutService.is_locked(email):
            remaining = LockoutService.get_remaining_lockout_seconds(email)
            logger.warning(
                f"Bloqueio ativo para email={masked}. Restante: {remaining}s"
            )
            raise AccountLockedError(
                f"Muitas tentativas com erro para a conta '{masked}'. Bloqueio ativo (lockout): tente novamente em {remaining} segundos.",
                code="account_locked",
            )

        user = authenticate(request=None, username=email, password=password)
        if user is None:
            TokenService._handle_auth_failure(
                email=email, password=password, masked=masked
            )

        # Sucesso: limpa contador de falhas acumuladas
        LockoutService.reset_failures(email)

        # ninja_jwt v5.4.5 alterou a assinatura de for_user
        refresh = RefreshToken.for_user(user)  # type: ignore[misc]
        token_out = TokenOut(
            access=str(refresh.access_token),
            refresh=str(refresh),
            user=UserDataOut(
                id=user.id,
                uuid=user.uuid,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                is_email_verified=user.is_email_verified,
            ),
        )

        logger.info(f"Token gerado com sucesso para user uuid={user.uuid}")
        return token_out

    @staticmethod
    def _handle_auth_failure(email: str, password: str, masked: str) -> None:
        """Trata falha de autenticação com timing attack mitigation e lockout."""
        from apps.users.models import User

        potential_user = User.objects.filter(email=email).first()
        if potential_user is None:
            # Mitigação de Timing Attack: executa hash dummy em tempo constante
            dummy_user = User()
            dummy_user.set_password("dummy_password_timing_defense")
            dummy_user.check_password(password)
            password_valid = False
        else:
            password_valid = potential_user.check_password(password)

        if potential_user and password_valid and not potential_user.is_email_verified:
            raise AuthenticationFailedError(
                f"Sua conta para '{masked}' ainda não foi ativada. "
                "Verifique sua caixa de entrada para confirmar seu e-mail.",
                code="email_not_verified",
            )

        LockoutService.record_failure(email)
        logger.warning(f"Falha de autenticação para email={masked}")
        raise AuthenticationFailedError(
            f"Credenciais inválidas ou conta desativada. Conta: '{masked}'.",
            code="invalid_credentials",
        )

    @staticmethod
    def logout(refresh_token: str) -> None:
        """Invalida o refresh token no servidor adicionando-o à blacklist do ninja_jwt.

        Decisão Arquitetural: [Fluxo JWT](docs/architecture/concepts/auth-jwt-flow.md)
        Efeitos Colaterais: Adiciona o refresh token à blacklist se válido.
        """
        token_fp = hashlib.sha256(refresh_token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de revogação/logout de token (fp={token_fp})")
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"Token adicionado à blacklist com sucesso (fp={token_fp})")
        except Exception as e:
            logger.warning(f"Falha ao invalidar token no logout (fp={token_fp}): {e}")

    @staticmethod
    def refresh(refresh_token: str) -> TokenRefreshOutputSchema:
        """Gera um novo par de tokens a partir de um refresh token com rotação ativa.

        Decisão Arquitetural: [Fluxo JWT](docs/architecture/concepts/auth-jwt-flow.md)
        Efeitos Colaterais: Invalida o refresh token anterior na blacklist.

        Raises:
            HttpError: Se o refresh token for inválido, expirado ou estiver na blacklist.
        """
        token_fp = hashlib.sha256(refresh_token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de refresh de token (fp={token_fp})")
        schema = TokenRefreshInputSchema(refresh=refresh_token)
        result = schema.to_response_schema()  # type: ignore[no-untyped-call]
        logger.info(f"Token refresh bem-sucedido (fp={token_fp})")
        return cast(TokenRefreshOutputSchema, result)

    @staticmethod
    def verify(token: str) -> VerifyTokenOut:
        """Verifica a integridade e a validade temporal de um token JWT.

        Decisão Arquitetural: [Fluxo JWT](docs/architecture/concepts/auth-jwt-flow.md)

        Raises:
            HttpError: Se o token for inválido, corrompido ou expirado.
        """
        token_fp = hashlib.sha256(token.encode()).hexdigest()[:12]
        logger.info(f"Tentativa de verificação de token (fp={token_fp})")
        schema = TokenVerifyInputSchema(token=token)
        # O método levanta HttpError(401) caso o token seja inválido.
        schema.to_response_schema()  # type: ignore[no-untyped-call]
        logger.info(f"Token verificado com sucesso (fp={token_fp})")
        return VerifyTokenOut()
