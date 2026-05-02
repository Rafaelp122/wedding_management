from django.db.models import QuerySet
from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingOut, WeddingPatchIn
from apps.weddings.services import WeddingService


# Utiliza django_auth para obrigar autenticação nos endpoints
router = Router(tags=["Weddings"])


@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
@paginate
def list_weddings(request: HttpRequest) -> QuerySet[Wedding]:
    """
    Lista todos os casamentos gerenciados pelo Planner logado.

    Retorna apenas os registros criados pelo usuário autenticado.
    Garante o isolamento de dados entre diferentes Planners (Multi-tenancy).
    """
    return WeddingService.list(user=request.user)


@router.get(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **READ_ERROR_RESPONSES},
    operation_id="weddings_read",
)
def retrieve_wedding(request: HttpRequest, uuid: UUID4) -> Wedding:
    """
    Retorna os detalhes completos de um casamento específico.

    Realiza a busca pelo UUID e valida se o registro pertence ao usuário.
    Caso não exista ou pertença a outro Planner, retorna um erro 404.
    """
    return WeddingService.get(user=request.user, uuid=uuid)


@router.post(
    "/",
    response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_create",
)
def create_wedding(request: HttpRequest, payload: WeddingIn) -> tuple[int, Wedding]:
    """
    Cria um novo casamento e inicializa sua estrutura financeira.

    Ao criar um casamento, o Service Layer automaticamente:
    - Associa o Planner logado como dono do registro.
    - Cria um **Budget (Orçamento)** inicial zerado para o evento.
    """
    wedding = WeddingService.create(user=request.user, data=payload.model_dump())
    return 201, wedding


@router.patch(
    "/{uuid:uuid}/",
    response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_partial_update",
)
def partial_update_wedding(
    request: HttpRequest,
    uuid: UUID4,
    payload: WeddingPatchIn,
) -> Wedding:
    """
    Atualiza informações específicas de um casamento.

    Permite modificar campos como nomes dos noivos, data e local sem afetar o restante.
    Os dados são validados pelo Service antes da persistência.
    """
    # Pega só os campos enviados (não nulos na requisição, exclude_unset)
    data = payload.model_dump(exclude_unset=True)

    updated_wedding = WeddingService.partial_update(
        user=request.user, uuid=uuid, data=data
    )
    return updated_wedding


@router.delete(
    "/{uuid:uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="weddings_delete",
)
def delete_wedding(request: HttpRequest, uuid: UUID4) -> tuple[int, None]:
    """
    Remove um casamento e limpa todos os dados vinculados (Cascata).

    **Atenção:** Esta ação é irreversível e deleta automaticamente:
    - Todo o histórico financeiro (orçamentos e despesas).
    - Cronogramas, contratos e fornecedores vinculados exclusivamente a este evento.
    """
    WeddingService.delete(user=request.user, uuid=uuid)
    return 204, None
