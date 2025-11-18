from typing import Any, Optional

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.shortcuts import redirect
from django.urls import reverse_lazy


class OwnerRequiredMixin(LoginRequiredMixin):
    """
    GENÉRICO (Core): Garante que o usuário esteja logado e que as
    operações (get_queryset) sejam restritas ao dono.

    A View/Mixin que herda DEVE fornecer:
    - self.model
    - self.owner_field_name (str): Ex: 'planner', 'user', 'owner'.
    """

    owner_field_name: Optional[str] = None
    model: Any = None  # Type hint para o modelo

    def get_queryset(self) -> QuerySet:
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        """
        # Valida se o Model existe
        if getattr(self, "model", None) is None:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define a 'model' attribute."
            )

        # Valida se o nome do campo dono existe
        if not self.owner_field_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define 'owner_field_name'."
            )

        # Obtém o queryset base
        # Nota: Usamos self.model.objects.all() para garantir um fresh start,
        # mas poderíamos usar super().get_queryset() se quiséssemos herdar
        # filtros anteriores.
        queryset = self.model.objects.all()

        # Filtra dinamicamente
        return queryset.filter(**{self.owner_field_name: self.request.user})


class RedirectAuthenticatedUserMixin:
    """
    Mixin para views públicas (Login, Signup, Home).\n
    Redireciona usuários já autenticados para a página
    principal de "meus casamentos".
    """

    # Define o destino do redirecionamento
    redirect_url_authenticated = reverse_lazy("weddings:my_weddings")

    # A mensagem base a ser exibida
    redirect_message = "Bem vindo de volta"

    def dispatch(self, request, *args, **kwargs):
        """
        Este método é executado ANTES do 'get' ou 'post' da view.
        """
        # Verifica se o utilizador está autenticado
        if request.user.is_authenticated:

            # Adiciona a mensagem de sucesso
            messages.success(
                self.request,
                f"{self.redirect_message},{request.user.first_name or
                                           request.user.username}!",
            )

            # Redireciona para a página principal
            return redirect(self.redirect_url_authenticated)

        # Se não estiver autenticado, continua para a view (Login/Signup)
        return super().dispatch(request, *args, **kwargs)
