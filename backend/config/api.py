"""
Main Django Ninja API configuration.
"""

from django.http import HttpRequest
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.core.exceptions import ApplicationError
from apps.finances.api import (
    BudgetCategoryController,
    BudgetController,
    ExpenseController,
    InstallmentController,
)
from apps.logistics.api import (
    ContractController,
    ItemController,
    SupplierController,
)
from apps.scheduler.api import EventController, TaskController
from apps.users.api import router as auth_router
from apps.weddings.api import WeddingController


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

# Registra os controllers das apps
api.register_controllers(
    WeddingController,
    # Finanças
    BudgetController,
    BudgetCategoryController,
    ExpenseController,
    InstallmentController,
    # Logística
    SupplierController,
    ContractController,
    ItemController,
    # Agenda
    EventController,
    TaskController,
)
