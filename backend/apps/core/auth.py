from apps.core.exceptions import BusinessRuleViolation
from apps.core.types import AuthContextUser
from apps.users.models import User


def require_user(user: AuthContextUser) -> User:
    if not user.is_authenticated:
        raise BusinessRuleViolation(
            detail="Autenticação obrigatória para executar esta operação.",
            code="authentication_required",
        )
    return user
