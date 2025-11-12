from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy


class RedirectAuthenticatedUserMixin:
    """
    Mixin para views públicas (Login, Signup, Home).
    Redireciona utilizadores já autenticados para a página
    principal de "meus casamentos".
    """

    # Define o destino do redirecionamento
    redirect_url_authenticated = reverse_lazy('weddings:my_weddings')

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
                f"{self.redirect_message}, {request.user.first_name or request.user.username}!"
            )

            # Redireciona para a página principal
            return redirect(self.redirect_url_authenticated)

        # Se não estiver autenticado, continua para a view (Login/Signup)
        return super().dispatch(request, *args, **kwargs)
