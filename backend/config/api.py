"""
Main Django Ninja API configuration.
"""

import logging

import sentry_sdk
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404, HttpRequest, HttpResponse
from ninja.errors import HttpError
from ninja.errors import ValidationError as NinjaValidationError
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from pydantic import ValidationError as PydanticValidationError

from apps.core.cron_api import cron_router
from apps.core.exceptions import ApplicationError
from apps.finances.api import (
    budget_categories_router,
    budgets_router,
    expenses_router,
    installments_router,
)
from apps.logistics.api import contracts_router, items_router, suppliers_router
from apps.scheduler.api import events_router as scheduler_events_router
from apps.scheduler.api import tasks_router as scheduler_tasks_router
from apps.users.api import router as auth_router
from apps.weddings.api import dashboard_router
from apps.weddings.api import router as weddings_router


logger = logging.getLogger(__name__)

# Instância principal do Django Ninja
# auth=JWTAuth() garante que todos os endpoints exigem Bearer JWT por padrão
api = NinjaExtraAPI(
    title="Wedding Management API (Ninja)",
    version="1.0.0",
    docs_url="/docs/",
    auth=JWTAuth(),
)


# --- Handler 1: O "Conversador" ---
# Trata tudo que previsto na Service Layer
@api.exception_handler(ApplicationError)
def application_error_handler(
    request: HttpRequest, exc: ApplicationError
) -> HttpResponse:
    return api.create_response(
        request,
        {"detail": exc.detail, "code": exc.code},
        status=exc.status_code,
    )


# --- Handler 2: Validação de modelo/serviço ---
# Django ValidationError vindo do model clean() ou service layer → HTTP 400.
@api.exception_handler(DjangoValidationError)
def django_validation_error_handler(
    request: HttpRequest, exc: DjangoValidationError
) -> HttpResponse:
    detail = (
        exc.message_dict
        if hasattr(exc, "message_dict") and exc.message_dict
        else exc.messages
        if hasattr(exc, "messages") and exc.messages
        else str(exc)
    )
    return api.create_response(
        request,
        {"detail": detail, "code": "validation_error"},
        status=400,
    )


# --- Handler 3: Erros HTTP do Ninja (401, 403, 404, 405, etc.) ---
@api.exception_handler(Http404)
def http_404_handler(request: HttpRequest, exc: Http404) -> HttpResponse:
    return api.create_response(
        request,
        {"detail": "Recurso não encontrado.", "code": "not_found"},
        status=404,
    )


@api.exception_handler(HttpError)
def http_error_handler(request: HttpRequest, exc: HttpError) -> HttpResponse:
    status_code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        422: "unprocessable_entity",
    }
    code = status_code_map.get(exc.status_code, "http_error")
    msg = str(getattr(exc, "message", exc))
    return api.create_response(
        request,
        {"detail": msg, "code": code},
        status=exc.status_code,
    )


# --- Handler 4: Erros de validação de payload (Pydantic / Ninja) ---
@api.exception_handler(NinjaValidationError)
@api.exception_handler(PydanticValidationError)
def validation_error_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
    if hasattr(exc, "errors"):
        err_attr = exc.errors
        errors = err_attr() if callable(err_attr) else err_attr
    else:
        errors = str(exc)
    return api.create_response(
        request,
        {"detail": errors, "code": "validation_error"},
        status=422,
    )


# --- Handler 5: O "Segurança" ---
# Trata o que NÃO foi previsto (bugs reais) → HTTP 500.
@api.exception_handler(Exception)
def general_exception_handler(request: HttpRequest, exc: Exception) -> HttpResponse:
    logger.exception("Unhandled exception in API")
    sentry_sdk.capture_exception(exc)

    return api.create_response(
        request,
        {"detail": "Erro interno do servidor.", "code": "internal_error"},
        status=500,
    )


@api.get("/health", auth=None, operation_id="core_health_check")
def health_check(request: HttpRequest):
    """
    Verifica a saúde do serviço e a conectividade com o banco de dados.
    Pode ser pingado por serviços externos de monitoramento.
    """
    from django.db import connection
    from django.db.utils import OperationalError

    try:
        connection.ensure_connection()
        return {"status": "healthy", "database": "up"}
    except OperationalError:
        return api.create_response(
            request,
            {"status": "unhealthy", "database": "down"},
            status=503,
        )


# Registra o router de autenticação customizado (retorna user data)
api.add_router("/auth/", auth_router, auth=None)

# Registra os routers das apps
api.add_router("/weddings/", weddings_router)
api.add_router("/dashboard/", dashboard_router)
api.add_router("/logistics/suppliers/", suppliers_router)
api.add_router("/logistics/contracts/", contracts_router)
api.add_router("/logistics/items/", items_router)

api.add_router("/finances/budgets/", budgets_router)
api.add_router("/finances/categories/", budget_categories_router)
api.add_router("/finances/expenses/", expenses_router)
api.add_router("/finances/installments/", installments_router)

api.add_router("/scheduler/events/", scheduler_events_router)
api.add_router("/scheduler/tasks/", scheduler_tasks_router)
api.add_router("/internal/cron/", cron_router, auth=None)
