from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from ..models import Event


class EventPlannerOwnerMixin(LoginRequiredMixin):
    """
    Mixin usado para restringir o acesso a eventos
    apenas ao planner (usuário) que os criou.
    """

    model = Event

    def get_queryset(self):
        # Filtra o queryset para incluir apenas os eventos do usuário logado
        print(f"DEBUG EventPlannerOwnerMixin: Filtrando queryset para planner ID: {self.request.user.id}")
        qs = super().get_queryset().filter(planner=self.request.user)
        print(f"DEBUG EventPlannerOwnerMixin: Queryset filtrada encontrada: {qs.count()} eventos.")
        return qs

    def get_object(self, queryset=None):
        # Busca o objeto e valida se o planner logado é o dono
        obj = super().get_object(queryset=queryset)
        if obj.planner != self.request.user:
            print(
                f"DEBUG EventPlannerOwnerMixin: Acesso NEGADO evento ID {obj.id} user ID {self.request.user.id}. Dono: {obj.planner.id}"
            )
            raise PermissionDenied("Você não tem permissão para acessar este evento.")
        print(
            f"DEBUG EventPlannerOwnerMixin: Acesso PERMITIDO evento ID {obj.id} user ID {self.request.user.id}"
        )
        return obj
