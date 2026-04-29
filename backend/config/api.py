from django.core.exceptions import ValidationError as DjangoValidationError
from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.events.api.event_controller import EventController
from apps.events.api.wedding_controller import WeddingController
from apps.finances.api.budget_controller import BudgetController
from apps.finances.api.category_controller import CategoryController
from apps.finances.api.expense_controller import ExpenseController
from apps.finances.api.installment_controller import InstallmentController
from apps.logistics.api.contracts import ContractController
from apps.logistics.api.items import ItemController
from apps.logistics.api.suppliers import SupplierController
from apps.scheduler.api.scheduler_controller import SchedulerController
from apps.users.api import AuthController


api = NinjaExtraAPI(
    title="Wedding Management API",
    version="1.0.0",
    description="API para gestão de casamentos e eventos",
    auth=JWTAuth(),
)

# Registro de Controllers
api.register_controllers(
    AuthController,
    BudgetController,
    CategoryController,
    ExpenseController,
    InstallmentController,
    SupplierController,
    ContractController,
    ItemController,
    SchedulerController,
    WeddingController,
    EventController,
)


# Handlers de Exceção Globais
@api.exception_handler(ObjectNotFoundError)
def on_object_not_found(request, exc):
    return api.create_response(
        request, {"detail": exc.detail, "code": exc.code}, status=404
    )


@api.exception_handler(DomainIntegrityError)
def on_domain_integrity_error(request, exc):
    return api.create_response(
        request, {"detail": exc.detail, "code": exc.code}, status=400
    )


@api.exception_handler(BusinessRuleViolation)
def on_business_rule_violation(request, exc):
    return api.create_response(
        request, {"detail": exc.detail, "code": exc.code}, status=422
    )


@api.exception_handler(DjangoValidationError)
def on_django_validation_error(request, exc):
    """Converte erros de validação do Django (Models) em 422."""
    return api.create_response(
        request, {"detail": exc.message_dict, "code": "validation_error"}, status=422
    )
