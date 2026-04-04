from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.weddings.schemas import WeddingIn, WeddingOut, WeddingPatchIn
from apps.weddings.services import WeddingService


# Utiliza django_auth para obrigar autenticação nos endpoints
router = Router(tags=["Weddings"])


@router.get("/", response=list[WeddingOut], operation_id="weddings_list")
@paginate
def list_weddings(request):
    """
    Lista todos os casamentos gerenciados pelo Planner logado.

    Retorna apenas os registros criados pelo usuário autenticado.
    Garante o isolamento de dados entre diferentes Planners (Multi-tenancy).
    """
    return WeddingService.list(user=request.user)


@router.get("/{uuid:uuid}/", response=WeddingOut, operation_id="weddings_read")
def retrieve_wedding(request, uuid: UUID4):
    """
    Retorna os detalhes completos de um casamento específico.

    Realiza a busca pelo UUID e valida se o registro pertence ao usuário.
    Caso não exista ou pertença a outro Planner, retorna um erro 404.
    """
    wedding = WeddingService.get(user=request.user, uuid=uuid)
    return wedding


@router.post("/", response={201: WeddingOut}, operation_id="weddings_create")
def create_wedding(request, payload: WeddingIn):
    """
    Cria um novo casamento e inicializa sua estrutura financeira.

    Ao criar um casamento, o Service Layer automaticamente:
    - Associa o Planner logado como dono do registro.
    - Cria um **Budget (Orçamento)** inicial zerado para o evento.
    """
    wedding = WeddingService.create(user=request.user, data=payload.model_dump())
    return 201, wedding


@router.patch(
    "/{uuid:uuid}/", response=WeddingOut, operation_id="weddings_partial_update"
)
def partial_update_wedding(request, uuid: UUID4, payload: WeddingPatchIn):
    """
    Atualiza informações específicas de um casamento.

    Permite modificar campos como nomes dos noivos, data e local sem afetar o restante.
    Os dados são validados pelo Service antes da persistência.
    """
    wedding = WeddingService.get(user=request.user, uuid=uuid)
    # Pega só os campos enviados (não nulos na requisição, exclude_unset)
    data = payload.model_dump(exclude_unset=True)

    updated_wedding = WeddingService.partial_update(
        user=request.user, instance=wedding, data=data
    )
    return updated_wedding


@router.delete("/{uuid:uuid}/", response={204: None}, operation_id="weddings_delete")
def delete_wedding(request, uuid: UUID4):
    """
    Remove um casamento e limpa todos os dados vinculados (Cascata).

    **Atenção:** Esta ação é irreversível e deleta automaticamente:
    - Todo o histórico financeiro (orçamentos e despesas).
    - Cronogramas, contratos e fornecedores vinculados exclusivamente a este evento.
    """
    wedding = WeddingService.get(user=request.user, uuid=uuid)
    WeddingService.delete(user=request.user, instance=wedding)
    return 204, None
