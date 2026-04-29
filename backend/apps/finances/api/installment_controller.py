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
from apps.finances.dependencies import get_installment
from apps.finances.models import Installment
from apps.finances.schemas import InstallmentIn, InstallmentOut, InstallmentPatchIn
from apps.finances.services.installment_service import InstallmentService


@api_controller("/finances/installments", tags=["Finances"])
class InstallmentController(ControllerBase):
    @http_get(
        "/", response=list[InstallmentOut], operation_id="finances_installments_list"
    )
    @paginate
    def list_installments(self) -> QuerySet[Installment]:
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return InstallmentService.list(self.context.request.user)

    @http_get(
        "/{installment_uuid}/",
        response={200: InstallmentOut, **READ_ERROR_RESPONSES},
        operation_id="finances_installments_read",
    )
    def get_installment(self, installment_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        return get_installment(self.context.request, installment_uuid)

    @http_post(
        "/",
        response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_create",
    )
    def create_installment(self, payload: InstallmentIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        assert self.context.request.user  # noqa: S101
        return 201, InstallmentService.create(
            self.context.request.user, payload.model_dump()
        )

    @http_patch(
        "/{installment_uuid}/",
        response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_update",
    )
    def update_installment(self, installment_uuid: UUID4, payload: InstallmentPatchIn):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_installment(self.context.request, installment_uuid)
        return InstallmentService.update(
            instance, payload.model_dump(exclude_unset=True)
        )

    @http_delete(
        "/{installment_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="finances_installments_delete",
    )
    def delete_installment(self, installment_uuid: UUID4):
        assert self.context  # noqa: S101
        assert self.context.request  # noqa: S101
        instance = get_installment(self.context.request, installment_uuid)
        InstallmentService.delete(instance)
        return 204, None
