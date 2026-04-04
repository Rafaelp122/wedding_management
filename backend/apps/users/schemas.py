from ninja import Schema
from pydantic import EmailStr


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
