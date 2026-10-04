from ninja import Schema
from pydantic import UUID4, ConfigDict, EmailStr, Field

from apps.users.models import User


class TokenPayloadIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(..., max_length=128)


class GoogleAuthIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    id_token: str


class UserDataOut(Schema):
    id: int
    uuid: UUID4
    email: str
    first_name: str
    last_name: str
    is_email_verified: bool = False


class TokenOut(Schema):
    access: str
    refresh: str
    user: UserDataOut


class RegisterIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    first_name: str = ""
    last_name: str = ""
    company_name: str = ""


class VerifyTokenOut(Schema):
    pass


class UserOut(Schema):
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
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


class PasswordResetConfirmIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    uid: str
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class PasswordResetResponseOut(Schema):
    message: str


class VerifyEmailIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    uid: str
    token: str


class ResendVerificationIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr


class VerifyEmailResponseOut(Schema):
    message: str


class LogoutIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    refresh: str


class LogoutOut(Schema):
    message: str
