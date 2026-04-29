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
from apps.finances.dependencies import get_budget_category
from apps.finances.models import BudgetCategory
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService


@api_controller("/finances/categories", tags=["Finances"])
class CategoryController(ControllerBase):
    @http_get(
        "/", response=list[BudgetCategoryOut], operation_id="finances_categories_list"
    )
    @paginate
    def list_categories(
        self, event_id: UUID4 | None = None
    ) -> QuerySet[BudgetCategory]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return BudgetCategoryService.list(self.context.request.user, event_id=event_id)

    @http_get(
        "/{category_uuid}/",
        response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
        operation_id="finances_categories_read",
    )
    def get_category(self, category_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_budget_category(self.context.request, category_uuid)

    @http_post(
        "/",
        response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_create",
    )
    def create_category(self, payload: BudgetCategoryIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, BudgetCategoryService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/{category_uuid}/",
        response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_update",
    )
    def update_category(self, category_uuid: UUID4, payload: BudgetCategoryPatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_budget_category(self.context.request, category_uuid)
        return BudgetCategoryService.update(
            instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{category_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_categories_delete",
    )
    def delete_category(self, category_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_budget_category(self.context.request, category_uuid)
        BudgetCategoryService.delete(instance)
        return 204, None
