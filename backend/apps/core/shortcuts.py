from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from apps.core.exceptions import ObjectNotFoundError
from apps.core.tenant import validate_tenant_ownership


if TYPE_CHECKING:
    from django.db.models import QuerySet

    from apps.tenants.models import Company


def _get_not_found_detail(model_cls: type[models.Model], detail: str | None) -> str:
    if detail:
        return detail

    model_name = getattr(model_cls._meta, "verbose_name", "Recurso")

    name_str = str(model_name).lower()
    suffix = (
        "encontrada"
        if name_str.endswith("a") or name_str.endswith("ão")
        else "encontrado"
    )

    return f"{model_name} não {suffix} ou acesso negado."


def _build_tenant_queryset[ModelT: models.Model](
    model_cls: type[ModelT],
    company: "Company",
    *,
    select_related: list[str] | None = None,
    prefetch_related: list[str] | None = None,
) -> "QuerySet[ModelT]":
    queryset = model_cls.objects.for_tenant(company)  # type: ignore[attr-defined]

    if select_related:
        queryset = queryset.select_related(*select_related)
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)

    return cast("QuerySet[ModelT]", queryset)


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
        queryset = _build_tenant_queryset(
            model_cls,
            company,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )

        return queryset.get(uuid=uuid)
    except (ObjectDoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail=_get_not_found_detail(model_cls, detail),
            code=code,
        ) from e


def resolve_tenant_resource[ModelT: models.Model](
    model_cls: type[ModelT],
    company: "Company",
    resource_input: ModelT | UUID | str,
    *,
    lookup_field: str = "uuid",
    select_related: list[str] | None = None,
    prefetch_related: list[str] | None = None,
    detail: str | None = None,
    code: str = "not_found_or_denied",
) -> ModelT:
    """
    Resolve uma instância ou identificador garantindo isolamento por tenant.

    Args:
        model_cls: Classe esperada do modelo Django.
        company: Tenant atual usado para validação e busca.
        resource_input: Instância pré-carregada, UUID ou string identificadora.
        lookup_field: Campo usado na busca quando o input é identificador.
        select_related: Relações FK para otimização da busca.
        prefetch_related: Relações reversas ou M2M para otimização da busca.
        detail: Mensagem de erro customizada.
        code: Código de erro customizado.

    Returns:
        A instância resolvida e pertencente ao tenant atual.

    Raises:
        ObjectNotFoundError: Se o recurso não existir, pertencer a outro tenant
            ou o tipo recebido não puder ser resolvido com segurança.
    """
    if isinstance(resource_input, model_cls):
        validate_tenant_ownership(
            company,
            resource_input,
            detail=_get_not_found_detail(model_cls, detail),
            code=code,
        )
        return resource_input

    if not isinstance(resource_input, UUID | str):
        raise ObjectNotFoundError(
            detail=_get_not_found_detail(model_cls, detail),
            code=code,
        )

    if lookup_field == "uuid":
        return get_object_or_404_for_tenant(
            model_cls,
            company,
            resource_input,
            select_related=select_related,
            prefetch_related=prefetch_related,
            detail=detail,
            code=code,
        )

    try:
        queryset = _build_tenant_queryset(
            model_cls,
            company,
            select_related=select_related,
            prefetch_related=prefetch_related,
        )

        return queryset.get(**{lookup_field: resource_input})
    except (ObjectDoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(
            detail=_get_not_found_detail(model_cls, detail),
            code=code,
        ) from e
