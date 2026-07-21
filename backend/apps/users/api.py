from typing import Any

from django.http import HttpRequest
from ninja_extra import Router
from ninja_extra.throttling import AnonRateThrottle
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.core.schemas import ErrorResponse

from .schemas import (
    GoogleAuthIn,
    RegisterIn,
    TokenOut,
    TokenPayloadIn,
    UserOut,
    VerifyTokenOut,
)
from .services.google_auth_service import GoogleAuthService
from .services.registration_service import RegistrationService
from .services.token_service import TokenService


class RegisterAnonThrottle(AnonRateThrottle):
    scope = "auth_register"


class LoginAnonThrottle(AnonRateThrottle):
    scope = "auth_login"


class RefreshAnonThrottle(AnonRateThrottle):
    scope = "auth_refresh"


class VerifyAnonThrottle(AnonRateThrottle):
    scope = "auth_verify"


class GoogleAuthAnonThrottle(AnonRateThrottle):
    scope = "auth_google"


router = Router(tags=["auth"])


@router.post(
    "/register/",
    response={201: UserOut, **MUTATION_ERROR_RESPONSES},
    auth=None,
    throttle=[RegisterAnonThrottle()],
    operation_id="auth_register_user",
)
def register_user(request: HttpRequest, payload: RegisterIn) -> tuple[int, Any]:
    """
    Cria um novo usuário e um workspace dedicado (Tenant Pragmático).
    """
    user = RegistrationService.register_new_owner(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
        company_name=payload.company_name,
    )
    return 201, user


@router.post(
    "/token/",
    response={200: TokenOut, 401: ErrorResponse, **MUTATION_ERROR_RESPONSES},
    auth=None,
    throttle=[LoginAnonThrottle()],
    operation_id="auth_obtain_token",
)
def obtain_token(request: HttpRequest, payload: TokenPayloadIn) -> TokenOut:
    """
    Autentica o usuário e retorna o token de acesso.

    Valida o email e senha no banco de dados.
    Se a conta estiver inativa ou as credenciais forem inválidas, retorna erro 401.
    No sucesso, retorna os tokens JWT e os dados básicos do usuário logado.
    """
    return TokenService.obtain(
        email=payload.email,
        password=payload.password,
    )


@router.post(
    "/refresh/",
    auth=None,
    throttle=[RefreshAnonThrottle()],
    response={
        200: TokenRefreshOutputSchema,
        401: ErrorResponse,
        **MUTATION_ERROR_RESPONSES,
    },
    operation_id="auth_refresh_token",
)
def refresh_token(
    request: HttpRequest, payload: TokenRefreshInputSchema
) -> TokenRefreshOutputSchema:
    """
    Gera um novo token de acesso usando um refresh token.

    Valida se o refresh token enviado ainda está no prazo de validade.
    Permite manter a sessão ativa sem o usuário precisar digitar a senha novamente.
    """
    return TokenService.refresh(payload.refresh)


@router.post(
    "/verify/",
    response={
        200: VerifyTokenOut,
        401: ErrorResponse,
        **MUTATION_ERROR_RESPONSES,
    },
    auth=None,
    throttle=[VerifyAnonThrottle()],
    operation_id="auth_verify_token",
)
def verify_token(
    request: HttpRequest, payload: TokenVerifyInputSchema
) -> VerifyTokenOut:
    """
    Verifica se um token ainda é válido e não expirou.

    Confere a assinatura do token JWT sem acessar o banco de dados.
    Ideal para o frontend checar o status do login antes de carregar uma página.
    """
    return TokenService.verify(payload.token)


@router.post(
    "/google/",
    response={200: TokenOut, 401: ErrorResponse, **MUTATION_ERROR_RESPONSES},
    auth=None,
    throttle=[GoogleAuthAnonThrottle()],
    operation_id="auth_google_login",
)
def google_login(request: HttpRequest, payload: GoogleAuthIn) -> TokenOut:
    """
    Autentica ou cadastra um usuário usando um ID Token do Google OAuth.

    Valida o token com os servidores do Google. Se o usuário já existir,
    retorna os tokens JWT. Caso contrário, registra o usuário e cria um workspace.
    """
    return GoogleAuthService.authenticate_with_google(payload.id_token)
