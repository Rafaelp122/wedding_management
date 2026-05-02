from typing import TYPE_CHECKING, Union

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest


if TYPE_CHECKING:
    from apps.users.models import User


AuthContextUser = Union["User", "AnonymousUser"]


class AuthRequest(HttpRequest):
    """
    Type Hinting Boundary para rotas autenticadas do Django Ninja.

    Informa ao Mypy que `request.user` é sempre uma instância do nosso User,
    eliminando avisos de AnonymousUser em endpoints protegidos por JWT.
    """

    user: "User"
