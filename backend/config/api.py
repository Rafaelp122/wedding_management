"""
Main Django Ninja API configuration.
"""

import logging

import sentry_sdk
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from pydantic import ValidationError as PydanticValidationError

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
def application_error_handler(request: HttpRequest, exc: ApplicationError):
    return api.create_response(
        request,
        {"detail": exc.detail, "code": exc.code},
        status=exc.status_code,
    )


# --- Handler 2: O "Segurança" ---
# Trata o que NÃO foi previsto (bugs reais).
# Re-raise Pydantic validation errors para não mascarar erros 422 do Ninja.
@api.exception_handler(Exception)
def general_exception_handler(request: HttpRequest, exc: Exception):
    if isinstance(exc, (PydanticValidationError, HttpError)):
        raise exc

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
