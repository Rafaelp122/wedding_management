from typing import TYPE_CHECKING

from apps.core.exceptions import ObjectNotFoundError

if TYPE_CHECKING:
    from apps.tenants.models import Company
    from django.db.models import Model


def validate_tenant_ownership(
    company: "Company",
    instance: "Model",
    *,
    detail: str = "Recurso não encontrado ou acesso negado.",
    code: str = "not_found_or_denied",
) -> None:
    if instance.company_id != company.id:
        raise ObjectNotFoundError(detail=detail, code=code)
