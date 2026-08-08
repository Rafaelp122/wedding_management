import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse

from apps.core.services import get_oidc_verifier


logger = logging.getLogger(__name__)


def require_oidc_auth(view_func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator limpo para exigir autenticação OIDC service-to-service (ADR-005).
    Delega a injeção de dependência para get_oidc_verifier().
    """

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")

        if not auth_header.startswith("Bearer "):
            logger.warning(
                "Cron request rejected: Missing Bearer token in Authorization header"
            )
            return JsonResponse(
                {"detail": "Token OIDC ausente.", "code": "missing_token"},
                status=401,
            )

        token = auth_header.replace("Bearer ", "").strip()

        try:
            verifier = get_oidc_verifier()
            claim = verifier.verify_token(token)
            logger.info("OIDC authentication successful for %s", claim.get("email"))
        except PermissionError as pe:
            return JsonResponse(
                {"detail": str(pe), "code": "unauthorized_sa"},
                status=403,
            )
        except Exception as e:
            logger.error("OIDC token verification failed: %s", e)
            return JsonResponse(
                {"detail": "Token OIDC inválido.", "code": "invalid_token"},
                status=403,
            )

        return view_func(request, *args, **kwargs)

    return wrapper
