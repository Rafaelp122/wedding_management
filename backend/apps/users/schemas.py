from ninja import Schema
from pydantic import UUID4, EmailStr


class TokenPayloadIn(Schema):
    email: EmailStr
    password: str


class UserDataOut(Schema):
    id: int
    email: str
    first_name: str
    last_name: str


class TokenOut(Schema):
    access: str
    refresh: str
    user: UserDataOut


class RegisterIn(Schema):
    """Schema para entrada de novos usuários (Owners)."""

    email: EmailStr
    password: str
    first_name: str = ""
    last_name: str = ""


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
