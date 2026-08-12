from ninja import Schema
from pydantic import UUID4, EmailStr, Field

from apps.users.models import User


class TokenPayloadIn(Schema):
    """Credenciais para autenticação (obtain token)."""

    email: EmailStr
    password: str


class GoogleAuthIn(Schema):
    """Payload para autenticação via Google OAuth2."""

    id_token: str


class UserDataOut(Schema):
    """Dados básicos do usuário retornados no token JWT."""

    id: int
    email: str
    first_name: str
    last_name: str
    is_email_verified: bool = False


class TokenOut(Schema):
    """Resposta de autenticação com tokens JWT e dados do usuário."""

    access: str
    refresh: str
    user: UserDataOut


class RegisterIn(Schema):
    """Schema para entrada de novos usuários (Owners)."""

    email: EmailStr
    password: str = Field(min_length=8)
    first_name: str = ""
    last_name: str = ""
    company_name: str = ""


class VerifyTokenOut(Schema):
    """Resposta vazia para verificação de token bem-sucedida."""

    pass


class UserOut(Schema):
    """Schema de saída simplificado do usuário."""

    uuid: UUID4
    email: str
    first_name: str
    last_name: str
    company_slug: str | None = None
    is_email_verified: bool = False

    @staticmethod
    def resolve_company_slug(obj: "User") -> str | None:
        return obj.company.slug if obj.company else None


class PasswordResetRequestIn(Schema):
    """Schema para solicitação de redefinição de senha."""

    email: EmailStr


class PasswordResetConfirmIn(Schema):
    """Schema para confirmação de redefinição de senha."""

    uid: str
    token: str
    new_password: str = Field(min_length=8)


class PasswordResetResponseOut(Schema):
    """Schema de resposta para operações de redefinição de senha."""

    message: str


class VerifyEmailIn(Schema):
    uid: str
    token: str


class ResendVerificationIn(Schema):
    email: EmailStr


class VerifyEmailResponseOut(Schema):
    message: str
