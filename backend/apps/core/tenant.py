from typing import TYPE_CHECKING

from apps.core.exceptions import ObjectNotFoundError


if TYPE_CHECKING:
    from django.db.models import Model

    from apps.tenants.models import Company


def validate_tenant_ownership(
    company: "Company",
    instance: "Model",
    *,
    detail: str = "Recurso não encontrado ou acesso negado.",
    code: str = "not_found_or_denied",
) -> None:
    """
    Verifica se a instância pertence ao tenant informado.

    Usada em métodos que recebem uma instância pré-carregada (update, delete, etc.)
    para garantir que o tenant que fez a requisição é o dono do recurso.
    Deve ser chamada antes de qualquer operação sobre a instância.

    Levanta ObjectNotFoundError (404) em vez de PermissionError (403) para não
    revelar a existência de recursos de outros tenants (segurança multi-tenant).
    """
    if instance.company_id != company.id:  # type: ignore[attr-defined]
        raise ObjectNotFoundError(detail=detail, code=code)
