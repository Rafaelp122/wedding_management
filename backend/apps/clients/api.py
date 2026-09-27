"""
Endpoints Ninja REST API para o domínio de clientes.
"""

from __future__ import annotations

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.clients.models import Client
from apps.clients.schemas import ClientIn, ClientOut, ClientPatchIn
from apps.clients.selectors import client_get_selector, client_list_selector
from apps.clients.services import ClientService
from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.users.types import AuthRequest


clients_router = Router(tags=["Clients"])


@clients_router.get("/", response=list[ClientOut], operation_id="list_clients")
@paginate
def list_clients(
    request: AuthRequest,
    q: str = "",
) -> QuerySet[Client]:
    """
    Lista todos os clientes cadastrados pela assessoria com paginação e busca textual.
    """
    user = request.user
    return client_list_selector(company=user.company, q=q)


@clients_router.post(
    "/",
    response={201: ClientOut, **MUTATION_ERROR_RESPONSES},
    operation_id="create_client",
)
def create_client(
    request: AuthRequest,
    payload: ClientIn,
) -> tuple[int, Client]:
    """
    Cadastra um novo cliente/contato no tenant autenticado.
    """
    user = request.user
    client = ClientService.create(company=user.company, payload=payload)
    return 201, client


@clients_router.get(
    "/{uuid:uuid}/",
    response={200: ClientOut, **READ_ERROR_RESPONSES},
    operation_id="get_client",
)
def get_client(request: AuthRequest, uuid: UUID4) -> Client:
    """
    Recupera os detalhes de um cliente específico pelo UUID.
    """
    user = request.user
    return client_get_selector(company=user.company, uuid=uuid)


@clients_router.patch(
    "/{uuid:uuid}/",
    response={200: ClientOut, **MUTATION_ERROR_RESPONSES},
    operation_id="update_client",
)
def update_client(
    request: AuthRequest,
    uuid: UUID4,
    payload: ClientPatchIn,
) -> Client:
    """
    Atualiza parcialmente os dados de um cliente existente.
    """
    user = request.user
    instance = client_get_selector(company=user.company, uuid=uuid)
    return ClientService.update(
        company=user.company, instance=instance, payload=payload
    )


@clients_router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="delete_client",
)
def delete_client(request: AuthRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove um cliente garantindo que não esteja vinculado a casamentos.
    """
    user = request.user
    instance = client_get_selector(company=user.company, uuid=uuid)
    ClientService.delete(company=user.company, instance=instance)
    return 204, None
