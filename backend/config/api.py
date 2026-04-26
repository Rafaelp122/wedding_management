"""
Main Django Ninja API configuration.
"""

from django.http import HttpRequest
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.core.exceptions import ApplicationError
from apps.finances.api.finances_controller import FinanceController
from apps.logistics.api.contracts import ContractController
from apps.logistics.api.items import ItemController
from apps.logistics.api.suppliers import SupplierController
from apps.scheduler.api.scheduler_controller import SchedulerController
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

# Registra os Controllers
api.register_controllers(
    WeddingController,
    SupplierController,
    ContractController,
    ItemController,
    FinanceController,
    SchedulerController,
)
