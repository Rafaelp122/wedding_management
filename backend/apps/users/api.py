from typing import Any, cast

from django.contrib.auth import authenticate
from django.http import HttpRequest
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.tokens import RefreshToken

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.core.schemas import ErrorResponse
from apps.users.schemas import TokenOut, TokenPayloadIn, UserDataOut


router = Router(tags=["auth"])


@router.post(
    "/token/",
    response={200: TokenOut, 401: ErrorResponse, **MUTATION_ERROR_RESPONSES},
    auth=None,
    operation_id="auth_obtain_token",
)
def obtain_token(request: HttpRequest, payload: TokenPayloadIn) -> TokenOut:
    """
    Autentica o usuário e retorna o token de acesso.

    Valida o email e senha no banco de dados.
    Se a conta estiver inativa ou as credenciais forem inválidas, retorna erro 401.
    No sucesso, retorna os tokens JWT e os dados básicos do usuário logado.
    """
    user = authenticate(request, username=payload.email, password=payload.password)

    if user is None:
        raise HttpError(401, "Credenciais inválidas ou conta desativada.")

    refresh = cast(Any, RefreshToken.for_user(user))

    return TokenOut(
        access=str(refresh.access_token),
        refresh=str(refresh),
        user=UserDataOut(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
        ),
    )


@router.post(
    "/refresh/",
    auth=None,
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
    return payload.to_response_schema()


@router.post(
    "/verify/",
    response={
        200: TokenRefreshOutputSchema,
        401: ErrorResponse,
        **MUTATION_ERROR_RESPONSES,
    },
    auth=None,
    operation_id="auth_verify_token",
)
def verify_token(
    request: HttpRequest, payload: TokenVerifyInputSchema
) -> TokenRefreshOutputSchema:
    """
    Verifica se um token ainda é válido e não expirou.

    Confere a assinatura do token JWT sem acessar o banco de dados.
    Ideal para o frontend checar o status do login antes de carregar uma página.
    """
    return payload.to_response_schema()
