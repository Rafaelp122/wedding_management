from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.models import BudgetCategory
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
)
from apps.finances.services import BudgetCategoryService


@api_controller("/finances/categories", tags=["Finances"])
class BudgetCategoryController(ControllerBase):
    def __init__(self, service: BudgetCategoryService):
        self.service = service

    @http_get(
        "/",
        response=list[BudgetCategoryOut],
        operation_id="finances_categories_list",
    )
    @paginate
    def list_categories(
        self, wedding_id: UUID4 | None = None
    ) -> QuerySet[BudgetCategory]:
        """Lista categorias de custo."""
        return self.service.list(self.context.request.user, wedding_id=wedding_id)

    @http_get(
        "/{uuid}/",
        response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
        operation_id="finances_categories_read",
    )
    def retrieve_category(self, uuid: UUID4) -> BudgetCategory:
        """Retorna detalhes de uma categoria."""
        return self.service.get(self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_create",
    )
    def create_category(self, payload: BudgetCategoryIn) -> tuple[int, BudgetCategory]:
        """Cria uma nova categoria orçamentária."""
        category = self.service.create(self.context.request.user, payload.model_dump())
        return 201, category

    @http_patch(
        "/{uuid}/",
        response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_partial_update",
    )
    def partial_update_category(
        self, uuid: UUID4, payload: BudgetCategoryPatchIn
    ) -> BudgetCategory:
        """Atualiza parcialmente uma categoria."""
        instance = self.service.get(self.context.request.user, uuid=uuid)
        return self.service.partial_update(
            self.context.request.user, instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_delete",
    )
    def delete_category(self, uuid: UUID4) -> tuple[int, None]:
        """Remove uma categoria."""
        self.service.delete(self.context.request.user, uuid)
        return 204, None
