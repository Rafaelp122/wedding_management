from apps.core.exceptions import BusinessRuleViolation

from .models import User
from .types import AuthContextUser


def require_user(user: AuthContextUser) -> User:
    """
    Garante que o usuário está autenticado e retorna a instância de User.
    Lança BusinessRuleViolation caso contrário.
    """
    if not user.is_authenticated:
        raise BusinessRuleViolation(
            detail="Autenticação obrigatória para executar esta operação.",
            code="authentication_required",
        )
    return user
