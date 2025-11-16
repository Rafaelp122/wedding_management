from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from apps.weddings.models import Wedding


class SchedulerWeddingMixin(LoginRequiredMixin):
    """
    Mixin para CBVs do Scheduler.

    1. Garante que o usuário esteja logado (LoginRequiredMixin).
    2. Busca o objeto 'Wedding' pelo 'wedding_id' da URL.
    3. Garante que o 'request.user' seja o 'planner' do casamento.
    4. Disponibiliza 'self.wedding' para as views.
    """

    wedding = None

    def dispatch(self, request, *args, **kwargs):
        # Busca o casamento
        wedding_id = self.kwargs.get("wedding_id")
        self.wedding = get_object_or_404(Wedding, id=wedding_id)

        # Verifica a permissão
        if self.wedding.planner != request.user:
            raise PermissionDenied(
                "Você não tem permissão para acessar este casamento."
            )

        # Continua para o método (get, post) da view
        return super().dispatch(request, *args, **kwargs)
