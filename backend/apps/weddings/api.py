from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import (
    ControllerBase,
    api_controller,
    http_delete,
    http_get,
    http_patch,
    http_post,
)
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingOut, WeddingPatchIn
from apps.weddings.services import WeddingService


@api_controller("/weddings", tags=["Weddings"])
class WeddingController(ControllerBase):
    """
    Controller para gerenciar a lógica de negócio de casamentos.
    Utiliza injeção de dependência e agrupa comportamentos relacionados.
    """

    def __init__(self, service: WeddingService):
        self.service = service

    @http_get("/", response=list[WeddingOut], operation_id="weddings_list")
    @paginate
    def list_weddings(self) -> QuerySet[Wedding]:
        """
        Lista todos os casamentos gerenciados pelo Planner logado.

        Retorna apenas os registros criados pelo usuário autenticado.
        Garante o isolamento de dados entre diferentes Planners (Multi-tenancy).
        """
        return self.service.list(user=self.context.request.user)

    @http_get(
        "/{uuid}/",
        response={200: WeddingOut, **READ_ERROR_RESPONSES},
        operation_id="weddings_read",
    )
    def retrieve_wedding(self, uuid: UUID4) -> Wedding:
        """
        Retorna os detalhes completos de um casamento específico.

        Realiza a busca pelo UUID e valida se o registro pertence ao usuário.
        Caso não exista ou pertença a outro Planner, retorna um erro 404.
        """
        return self.service.get(user=self.context.request.user, uuid=uuid)

    @http_post(
        "/",
        response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_create",
    )
    def create_wedding(self, payload: WeddingIn) -> tuple[int, Wedding]:
        """
        Cria um novo casamento e inicializa sua estrutura financeira.

        Ao criar um casamento, o Service Layer automaticamente:
        - Associa o Planner logado como dono do registro.
        - Cria um **Budget (Orçamento)** inicial zerado para o evento.
        """
        wedding = self.service.create(
            user=self.context.request.user, data=payload.model_dump()
        )
        return 201, wedding

    @http_patch(
        "/{uuid}/",
        response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_partial_update",
    )
    def partial_update_wedding(self, uuid: UUID4, payload: WeddingPatchIn) -> Wedding:
        """
        Atualiza informações específicas de um casamento.

        Permite modificar campos como nomes dos noivos, data e local sem afetar
        o restante. Os dados são validados pelo Service antes da persistência.
        """
        # Pega só os campos enviados (não nulos na requisição, exclude_unset)
        data = payload.model_dump(exclude_unset=True)

        updated_wedding = self.service.partial_update(
            user=self.context.request.user, uuid=uuid, data=data
        )
        return updated_wedding

    @http_delete(
        "/{uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_delete",
    )
    def delete_wedding(self, uuid: UUID4) -> tuple[int, None]:
        """
        Remove um casamento e limpa todos os dados vinculados (Cascata).

        **Atenção:** Esta ação é irreversível e deleta automaticamente:
        - Todo o histórico financeiro (orçamentos e despesas).
        - Cronogramas, contratos e fornecedores vinculados exclusivamente a este evento.
        """
        self.service.delete(user=self.context.request.user, uuid=uuid)
        return 204, None
