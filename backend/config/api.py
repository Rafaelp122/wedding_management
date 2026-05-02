"""
Main Django Ninja API configuration.
"""

from django.http import HttpRequest
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

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
from apps.weddings.api import router as weddings_router


# Instância principal do Django Ninja
# auth=JWTAuth() garante que todos os endpoints exigem Bearer JWT por padrão
api = NinjaExtraAPI(
    title="Wedding Management API (Ninja)",
    version="1.0.0",
    docs_url="/docs/",
    auth=JWTAuth(),
)


@api.exception_handler(ApplicationError)
def application_error_handler(request: HttpRequest, exc: ApplicationError):
    return api.create_response(
        request,
        {"detail": exc.detail, "code": exc.code},
        status=exc.status_code,
    )


# Registra o router de autenticação customizado (retorna user data)
api.add_router("/auth/", auth_router, auth=None)

# Registra os routers das apps
api.add_router("/weddings/", weddings_router)
api.add_router("/logistics/suppliers/", suppliers_router)
api.add_router("/logistics/contracts/", contracts_router)
api.add_router("/logistics/items/", items_router)

api.add_router("/finances/budgets/", budgets_router)
api.add_router("/finances/categories/", budget_categories_router)
api.add_router("/finances/expenses/", expenses_router)
api.add_router("/finances/installments/", installments_router)

api.add_router("/scheduler/events/", scheduler_events_router)
api.add_router("/scheduler/tasks/", scheduler_tasks_router)
