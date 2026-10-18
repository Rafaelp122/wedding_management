"""
Seletores de leitura para o domínio de Tenants (Empresas).
"""

from __future__ import annotations

from uuid import UUID

from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company


def company_get_selector(*, uuid: UUID | str) -> Company:
    """Recupera uma empresa (tenant) pelo seu identificador público UUID.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)

    Raises:
        ObjectNotFoundError: Se nenhuma empresa for encontrada com o UUID fornecido.
    """
    company = Company.objects.filter(uuid=uuid).first()
    if not company:
        raise ObjectNotFoundError(detail=f"Empresa com UUID '{uuid}' não encontrada.")
    return company
