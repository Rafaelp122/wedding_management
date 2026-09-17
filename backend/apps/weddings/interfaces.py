"""Interfaces públicas para o Bounded Context de Casamentos (apps.weddings).

Seguindo a ADR-031, este arquivo expõe exclusivamente os contratos de consulta
e mutação que outros domínios podem consumir, preservando o encapsulamento interno.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.weddings.models import Wedding


if TYPE_CHECKING:
    from apps.tenants.models import Company


def get_wedding_display_name(
    company: Company,
    wedding_uuid: UUID | str,
) -> str | None:
    """Recupera o nome formatado de exibição do casamento com isolamento multitenant.

    Args:
        company: Empresa (tenant) proprietária do registro.
        wedding_uuid: UUID identificador do casamento.

    Returns:
        str | None: Nome formatado ou None se não encontrado.
    """
    wedding = (
        Wedding.objects.for_tenant(company)
        .filter(uuid=wedding_uuid)
        .only("bride_name", "groom_name")
        .first()
    )
    if not wedding:
        return None
    return f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
