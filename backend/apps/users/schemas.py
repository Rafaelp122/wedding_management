from ninja import Schema
from pydantic import UUID4


class RegisterIn(Schema):
    """Schema para entrada de novos usuários (Owners)."""

    email: str
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
