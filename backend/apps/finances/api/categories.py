from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models.budget_category import BudgetCategory
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
)
from apps.finances.selectors import (
    budget_category_get_selector,
    budget_category_list_selector,
)
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.users.types import AuthRequest


budget_categories_router = Router(tags=["Finances"])


@budget_categories_router.get(
    "/", response=list[BudgetCategoryOut], operation_id="finances_categories_list"
)
@paginate
def list_categories(
    request: AuthRequest, wedding_id: UUID4 | None = None
) -> QuerySet[BudgetCategory]:
    """Lista as categorias de orçamento do tenant com filtros opcionais."""
    user = request.user
    return budget_category_list_selector(company=user.company, wedding_id=wedding_id)


@budget_categories_router.get(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
    operation_id="finances_categories_read",
)
def get_category(request: AuthRequest, uuid: UUID4) -> BudgetCategory:
    """Recupera detalhes de uma categoria de orçamento específica."""
    user = request.user
    return budget_category_get_selector(company=user.company, uuid=uuid)


@budget_categories_router.post(
    "/",
    response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_create",
)
def create_category(
    request: AuthRequest, payload: BudgetCategoryIn
) -> tuple[int, BudgetCategory]:
    """Cria uma nova categoria orçamentária vinculada a um orçamento."""
    user = request.user
    created = BudgetCategoryService.create(user.company, payload)
    return 201, budget_category_get_selector(company=user.company, uuid=created.uuid)


@budget_categories_router.patch(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_update",
)
def update_category(
    request: AuthRequest, uuid: UUID4, payload: BudgetCategoryPatchIn
) -> BudgetCategory:
    """Atualiza nome, descrição ou verba alocada de uma categoria."""
    user = request.user
    instance = budget_category_get_selector(company=user.company, uuid=uuid)
    BudgetCategoryService.update(user.company, instance, payload)
    return budget_category_get_selector(company=user.company, uuid=instance.uuid)


@budget_categories_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_delete",
)
def delete_category(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """Exclui uma categoria de orçamento sem despesas vinculadas."""
    user = request.user
    instance = budget_category_get_selector(company=user.company, uuid=uuid)
    BudgetCategoryService.delete(user.company, instance)
    return 204, None
