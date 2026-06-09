from ninja import Schema
from pydantic import UUID4, EmailStr, Field


class TokenPayloadIn(Schema):
    """Credenciais para autenticação (obtain token)."""

    email: EmailStr
    password: str


class UserDataOut(Schema):
    """Dados básicos do usuário retornados no token JWT."""

    id: int
    email: str
    first_name: str
    last_name: str


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

    @staticmethod
    def resolve_company_slug(obj):
        return obj.company.slug if obj.company else None
