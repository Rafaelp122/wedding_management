from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from apps.core.exceptions import ObjectNotFoundError


if TYPE_CHECKING:
    from apps.tenants.models import Company


def get_object_or_404_for_tenant[ModelT: models.Model](
    model_cls: type[ModelT],
    company: "Company",
    uuid: UUID | str,
    *,
    select_related: list[str] | None = None,
    prefetch_related: list[str] | None = None,
    detail: str | None = None,
    code: str = "not_found_or_denied",
) -> ModelT:
    """
    Busca um objeto pelo UUID e garante que ele pertence ao tenant (company).
    Levanta ObjectNotFoundError (404) caso não encontre ou pertença a outro tenant.

    Args:
        model_cls: Classe do modelo Django.
        company: Instância da empresa dona do recurso.
        uuid: UUID público do objeto.
        select_related: Lista de FKs para otimização de JOIN.
        prefetch_related: Lista de relações para otimização de M2M/Reverse FK.
        detail: Mensagem de erro customizada.
        code: Código de erro customizado.
    """
    try:
        # Assumimos que o model_cls tem o TenantManager (objects)
        # que implementa o método for_tenant.
        queryset = model_cls.objects.for_tenant(company)  # type: ignore[attr-defined]

        if select_related:
            queryset = queryset.select_related(*select_related)
        if prefetch_related:
            queryset = queryset.prefetch_related(*prefetch_related)

        return cast(ModelT, queryset.get(uuid=uuid))
    except (ObjectDoesNotExist, ValueError, ValidationError) as e:
        model_name = getattr(model_cls._meta, "verbose_name", "Recurso")
        error_detail = detail or f"{model_name} não encontrado ou acesso negado."
        raise ObjectNotFoundError(detail=error_detail, code=code) from e
