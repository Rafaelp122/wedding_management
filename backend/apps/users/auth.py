from apps.core.exceptions import BusinessRuleViolation
from apps.users.models import User
from apps.users.types import AuthContextUser


def require_user(user: AuthContextUser) -> User:
    if not user.is_authenticated:
        raise BusinessRuleViolation(
            detail="Autenticação obrigatória para executar esta operação.",
            code="authentication_required",
        )
    return user
