"""
Seletores de leitura para o domínio de Tenants (Empresas).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company


if TYPE_CHECKING:
    pass


def company_get_selector(*, uuid: UUID | str) -> Company:
    """Recupera uma empresa (tenant) pelo seu identificador público UUID.

    Args:
        uuid: Identificador UUID único da empresa.

    Returns:
        Company: Instância da empresa encontrada.

    Raises:
        ObjectNotFoundError: Se nenhuma empresa for encontrada com o UUID fornecido.
    """
    company = Company.objects.filter(uuid=uuid).first()
    if not company:
        raise ObjectNotFoundError(detail="Empresa não encontrada.")
    return company
