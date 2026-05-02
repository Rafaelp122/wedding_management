from typing import Any

from django.http import HttpRequest
from ninja import Router

from .schemas import RegisterIn, UserOut
from .services.registration_service import RegistrationService


router = Router(tags=["Autenticação"])


@router.post("/register/", response={201: UserOut})
def register_user(request: HttpRequest, payload: RegisterIn) -> tuple[int, Any]:
    """
    Cria um novo usuário e um workspace dedicado (Tenant Pragmático).
    """
    user = RegistrationService.register_new_owner(
        email=payload.email,
        password=payload.password,
        first_name=payload.first_name,
        last_name=payload.last_name,
    )
    return 201, user
