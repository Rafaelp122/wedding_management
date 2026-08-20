import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest

from apps.core.exceptions import AuthenticationFailedError, PermissionDeniedError
from apps.core.services import get_oidc_verifier


logger = logging.getLogger(__name__)


def require_oidc_auth[R](view_func: Callable[..., R]) -> Callable[..., R]:
    """
    Decorator limpo para exigir autenticação OIDC service-to-service (ADR-005).
    Delega a injeção de dependência para get_oidc_verifier().
    Lança ApplicationErrors (401/403) capturadas no pipeline do Django Ninja.
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> R:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            logger.warning(
                "Cron request rejected: Missing Bearer token in Authorization header"
            )
            raise AuthenticationFailedError(
                detail="Token OIDC ausente.",
                code="missing_token",
            )

        token = auth_header.replace("Bearer ", "").strip()

        try:
            verifier = get_oidc_verifier()
            claim = verifier.verify_token(token)
            logger.info("OIDC authentication successful for %s", claim.get("email"))
        except PermissionError as pe:
            logger.warning("OIDC: SA não autorizada - %s", pe)
            raise PermissionDeniedError(
                detail="Service account não autorizada.",
                code="unauthorized_sa",
            ) from None
        except Exception as e:
            logger.error("OIDC token verification failed: %s", type(e).__name__)
            raise PermissionDeniedError(
                detail="Token OIDC inválido.",
                code="invalid_token",
            ) from None

        return view_func(request, *args, **kwargs)

    return wrapper
