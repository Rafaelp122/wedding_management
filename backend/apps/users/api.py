from typing import Any, cast

from django.contrib.auth import authenticate
from ninja.errors import HttpError
from ninja_extra import ControllerBase, api_controller, http_post
from ninja_jwt.schema import (
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
    TokenVerifyInputSchema,
)
from ninja_jwt.tokens import RefreshToken

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.core.schemas import ErrorResponse
from apps.users.models import User
from apps.users.schemas import TokenOut, TokenPayloadIn, UserDataOut, UserRegisterIn


@api_controller("/auth", tags=["auth"])
class AuthController(ControllerBase):
    @http_post(
        "/token/",
        response={200: TokenOut, 401: ErrorResponse, **MUTATION_ERROR_RESPONSES},
        auth=None,
        operation_id="auth_obtain_token",
    )
    def obtain_token(self, payload: TokenPayloadIn) -> TokenOut:
        """
        Autentica o usuário e retorna o token de acesso.
        """
        user = authenticate(
            self.context.request, username=payload.email, password=payload.password
        )

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

    @http_post(
        "/register/",
        auth=None,
        response={201: TokenOut, 400: ErrorResponse, **MUTATION_ERROR_RESPONSES},
        operation_id="auth_register",
    )
    def register_user(self, payload: UserRegisterIn) -> tuple[int, TokenOut]:
        """
        Cria uma nova conta de usuário com Tenant Silencioso.
        """
        if User.objects.filter(email=payload.email).exists():
            raise HttpError(400, "Este email já está cadastrado.")

        user = User.objects.create_user(**payload.model_dump())

        refresh = cast(Any, RefreshToken.for_user(user))

        return 201, TokenOut(
            access=str(refresh.access_token),
            refresh=str(refresh),
            user=UserDataOut(
                id=user.id,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
            ),
        )

    @http_post(
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
        self, payload: TokenRefreshInputSchema
    ) -> TokenRefreshOutputSchema:
        """Gera um novo token de acesso usando um refresh token."""
        return payload.to_response_schema()

    @http_post(
        "/verify/",
        response={
            200: TokenRefreshOutputSchema,
            401: ErrorResponse,
            **MUTATION_ERROR_RESPONSES,
        },
        auth=None,
        operation_id="auth_verify_token",
    )
    def verify_token(self, payload: TokenVerifyInputSchema) -> TokenRefreshOutputSchema:
        """Verifica se um token ainda é válido."""
        return payload.to_response_schema()
