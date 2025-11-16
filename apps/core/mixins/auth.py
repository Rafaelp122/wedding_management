from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured


class OwnerRequiredMixin(LoginRequiredMixin):
    """
    GENÉRICO (Core): Garante que o usuário esteja logado e que as
    operações (get_queryset) sejam restritas ao dono.

    A View/Mixin que herda DEVE fornecer:
    - self.model
    - self.owner_field_name (str): Ex: 'planner', 'user', 'owner'.
    """

    owner_field_name = None

    def get_queryset(self):
        """
        Método de segurança padrão (usado por UpdateView, DeleteView).
        """
        if not hasattr(self, "model"):
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a 'model' attribute."
            )
        if not self.owner_field_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define 'owner_field_name'."
            )

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
