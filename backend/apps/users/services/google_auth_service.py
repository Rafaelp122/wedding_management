import logging

from django.db import transaction
from ninja.errors import HttpError
from ninja_jwt.tokens import RefreshToken

from apps.core.services.social_auth import GoogleOAuthProvider, OAuthUserInfo
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

        provider = GoogleOAuthProvider()
        user_info = provider.verify_token(id_token)

        user = GoogleAuthService._get_or_create_user(user_info)

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

        logger.info(f"Autenticação via Google concluída para o usuário: {user.email}")
        return token_out

    @staticmethod
    @transaction.atomic
    def _get_or_create_user(user_info: OAuthUserInfo) -> User:
        """
        Busca um usuário existente ou cadastra um novo com tenant no banco de dados.

        Args:
            user_info: As informações do usuário obtidas do provedor OAuth.

        Returns:
            A instância de User recuperada ou recém-criada.

        Raises:
            HttpError: Se a conta do usuário existente estiver desativada.
        """
        user = User.objects.filter(email=user_info.email).first()

        if user:
            if not user.is_active:
                logger.warning(
                    f"Tentativa de login via Google (conta inativa): {user_info.email}"
                )
                raise HttpError(401, "Credenciais inválidas ou conta desativada.")
        else:
            logger.info(
                f"Provisionando novo usuário via Google OAuth: {user_info.email}"
            )
            random_password = User.objects.make_random_password()
            display_name = (
                f"{user_info.first_name} {user_info.last_name}".strip()
                or user_info.email
            )
            company = TenantService.create_company(display_name=display_name)

            user = User.objects.create_user(
                email=user_info.email,
                password=random_password,
                company=company,
                first_name=user_info.first_name,
                last_name=user_info.last_name,
                is_active=True,
            )

        return user
