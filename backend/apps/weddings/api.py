from typing import Any

from django.db.models import QuerySet
from ninja.pagination import paginate
from ninja_extra import ControllerBase, api_controller, route
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.weddings.dependencies import get_wedding
from apps.weddings.models import Wedding
from apps.weddings.schemas import WeddingIn, WeddingOut, WeddingPatchIn
from apps.weddings.services import WeddingService


@api_controller("/weddings", tags=["Weddings"])
class WeddingController(ControllerBase):
    context: Any  # Para satisfazer o MyPy

    @route.get("/", response=list[WeddingOut], operation_id="weddings_list")
    @paginate
    def list_weddings(self) -> QuerySet[Wedding]:
        """
        Lista todos os casamentos gerenciados pelo Planner logado.
        """
        return WeddingService.list(user=self.context.request.user)

    @route.get(
        "/{wedding_uuid}/",
        response={200: WeddingOut, **READ_ERROR_RESPONSES},
        operation_id="weddings_read",
    )
    def retrieve_wedding(self, wedding_uuid: UUID4) -> Wedding:
        """
        Retorna os detalhes completos de um casamento específico.
        """
        wedding = get_wedding(self.context.request, wedding_uuid)
        return wedding

    @route.post(
        "/",
        response={201: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_create",
    )
    def create_wedding(self, payload: WeddingIn) -> tuple[int, Wedding]:
        """
        Cria um novo casamento e inicializa sua estrutura financeira.
        """
        wedding = WeddingService.create(
            user=self.context.request.user, data=payload.model_dump()
        )
        return 201, wedding

    @route.patch(
        "/{wedding_uuid}/",
        response={200: WeddingOut, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_update",
    )
    def update_wedding(
        self,
        wedding_uuid: UUID4,
        payload: WeddingPatchIn,
    ) -> Wedding:
        """
        Atualiza informações específicas de um casamento.
        """
        wedding = get_wedding(self.context.request, wedding_uuid)
        data = payload.model_dump(exclude_unset=True)
        return WeddingService.update(instance=wedding, data=data)

    @route.delete(
        "/{wedding_uuid}/",
        response={204: None, **MUTATION_ERROR_RESPONSES},
        operation_id="weddings_delete",
    )
    def delete_wedding(self, wedding_uuid: UUID4) -> tuple[int, None]:
        """
        Remove um casamento e limpa todos os dados vinculados (Cascata).
        """
        wedding = get_wedding(self.context.request, wedding_uuid)
        WeddingService.delete(instance=wedding)
        return 204, None
