from typing import TYPE_CHECKING

from django.db import models

from apps.core.exceptions import ObjectNotFoundError


if TYPE_CHECKING:
    from apps.tenants.models import Company


def validate_tenant_ownership[ModelT: models.Model](
    company: "Company",
    instance: ModelT,
    *,
    detail: str = "Recurso não encontrado ou acesso negado.",
    code: str = "not_found_or_denied",
) -> ModelT:
    """Verifica se uma instância pré-carregada pertence ao tenant informado.

    Serviços que recebem instâncias diretamente precisam validar o tenant antes
    de ler ou alterar o recurso, preservando a semântica de 404 para não revelar
    a existência de dados de outra empresa.

    Args:
        company: Empresa do usuário autenticado.
        instance: Modelo tenant-owned já carregado pelo chamador.
        detail: Mensagem segura retornada quando o tenant não confere.
        code: Código de erro seguro retornado quando o tenant não confere.

    Returns:
        A própria instância validada, permitindo uso em expressões.

    Raises:
        ObjectNotFoundError: Se a instância pertencer a outro tenant.
    """
    if getattr(instance, "company_id", None) != company.id:
        raise ObjectNotFoundError(detail=detail, code=code)
    return instance
