"""
Fachada pública do contexto Clients para comunicação entre Bounded Contexts (ADR-031).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import get_object_or_404_for_tenant


if TYPE_CHECKING:
    from apps.clients.models import Client
    from apps.tenants.models import Company


def get_client_for_tenant(company: Company, client_id: UUID | str) -> Client:
    """
    Recupera um cliente validando o isolamento do tenant para outros contextos.

    Args:
        company: Instância da empresa (Tenant) para isolamento.
        client_id: Identificador único (UUID) do cliente.

    Returns:
        Instância do modelo Client encontrada e pertencente à empresa.

    Raises:
        ObjectNotFoundError: Se o cliente não existir ou pertencer a outra empresa.
    """
    from apps.clients.models import Client

    return get_object_or_404_for_tenant(Client, company, uuid=client_id)


def get_or_create_client_for_proposal(
    company: Company,
    name: str,
    cpf: str = "",
    email: str = "",
    phone: str = "",
) -> Client:
    """
    Obtém um cliente existente por CPF, e-mail ou nome para o tenant, ou cria um novo cliente.

    Args:
        company: O tenant atual para isolamento de dados.
        name: Nome completo do cliente/contratante.
        cpf: CPF do cliente (opcional).
        email: E-mail de contato (opcional).
        phone: Telefone de contato (opcional).

    Returns:
        Instância de Client persistida.
    """
    from apps.clients.models import Client

    clean_name = name.strip() if name else ""
    clean_cpf = cpf.strip() if cpf else ""
    clean_email = email.strip().lower() if email else ""
    clean_phone = phone.strip() if phone else ""

    client = None
    qs = Client.objects.for_tenant(company)
    if clean_cpf:
        client = qs.filter(cpf=clean_cpf).first()
    if not client and clean_email:
        client = qs.filter(email=clean_email).first()
    if not client and clean_name:
        client = qs.filter(name=clean_name).first()

    if not client:
        client = Client(
            company=company,
            name=clean_name,
            cpf=clean_cpf,
            email=clean_email,
            phone=clean_phone,
        )
        client.save()
    else:
        updated = False
        if not client.cpf and clean_cpf:
            client.cpf = clean_cpf
            updated = True
        if not client.email and clean_email:
            client.email = clean_email
            updated = True
        if not client.phone and clean_phone:
            client.phone = clean_phone
            updated = True
        if updated:
            client.save()

    return client


__all__ = [
    "get_client_for_tenant",
    "get_or_create_client_for_proposal",
]
