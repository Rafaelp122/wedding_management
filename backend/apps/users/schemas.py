from ninja import Schema
from pydantic import EmailStr, Field


class TokenPayloadIn(Schema):
    email: EmailStr
    password: str


class UserDataOut(Schema):
    id: int
    email: EmailStr
    first_name: str
    last_name: str


class TokenOut(Schema):
    access: str
    refresh: str
    user: UserDataOut


class UserRegisterIn(Schema):
    """Schema para criação de nova conta."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
