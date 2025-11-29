from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy


class OwnerRequiredMixin(LoginRequiredMixin):
    """
    GENÉRICO (Core): Garante que o usuário esteja logado e que as
    operações (get_queryset) sejam restritas ao dono.

    Este mixin combina autenticação com autorização baseada em
    propriedade, garantindo que usuários só acessem seus próprios
    recursos.

    Attributes:
        owner_field_name: Nome do campo no modelo que representa o
                         proprietário.
                         Ex: 'planner', 'user', 'owner', 'created_by'.
        model: O modelo Django que será filtrado.

    Usage:
        class MyView(OwnerRequiredMixin, UpdateView):
            model = MyModel
            owner_field_name = 'user'

    A View/Mixin que herda DEVE fornecer:
    - self.model: O modelo Django
    - self.owner_field_name (str): Nome do campo que referencia o
                                   proprietário
    """

    owner_field_name: str | None = None
    model: type[Model] | None = None
    request: HttpRequest

    def get_queryset(self) -> "QuerySet[Any, Any]":
        """
        Filtra o queryset para retornar apenas objetos pertencentes
        ao usuário atual.

        Returns:
            QuerySet filtrado pelo proprietário (usuário logado).

        Raises:
            ImproperlyConfigured: Se 'model' ou 'owner_field_name'
                                 não estiverem definidos.
        """
        # Valida se o Model existe
        if not self.model:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define a 'model' attribute."
            )

        # Valida se o nome do campo dono existe
        if not self.owner_field_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define 'owner_field_name'."
            )

        # Nota: Usamos self.model.objects.all() para garantir um
        # fresh start, mas poderíamos usar super().get_queryset()
        # se quiséssemos herdar filtros anteriores.
        queryset = self.model.objects.all()

        # Filtra dinamicamente pelo proprietário
        return queryset.filter(**{self.owner_field_name: self.request.user})


class RedirectAuthenticatedUserMixin:
    """
    Mixin para views públicas (Login, Signup, Home).

    Redireciona usuários já autenticados para a página
    principal de "meus casamentos", evitando que acessem
    páginas de login/registro quando já estão logados.

    Attributes:
        redirect_url_authenticated: URL para onde redirecionar
                                   usuários autenticados.
        redirect_message: Mensagem de boas-vindas a ser exibida.

    Usage:
        class LoginView(RedirectAuthenticatedUserMixin, FormView):
            template_name = 'login.html'
            # Usuários já autenticados serão redirecionados
    """

    # Define o destino do redirecionamento
    redirect_url_authenticated = reverse_lazy("weddings:my_weddings")

    # A mensagem base a ser exibida
    redirect_message = "Bem vindo de volta"

    request: HttpRequest

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Intercepta a requisição antes de processar a view.

        Se o usuário estiver autenticado, redireciona para a área
        logada. Caso contrário, permite o acesso normal à view.

        Args:
            request: Objeto HttpRequest do Django.
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados.

        Returns:
            HttpResponse: Redirecionamento ou resposta normal da view.
        """
        # Verifica se o utilizador está autenticado
        if request.user.is_authenticated:
            # Obtém o nome de exibição (first_name ou username)
            first_name = getattr(request.user, "first_name", "")
            username = getattr(request.user, "username", "")
            display_name = str(first_name or username)

            # Adiciona a mensagem de sucesso (corrigido o espaço)
            messages.success(
                self.request,
                f"{self.redirect_message}, {display_name}!",
            )

            # Redireciona para a página principal
            return redirect(str(self.redirect_url_authenticated))

        # Se não estiver autenticado, continua para a view
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]


class WeddingOwnershipMixin(LoginRequiredMixin):
    """
    GENÉRICO (Core): Garante que o usuário logado seja o planner
    (dono) do casamento especificado na URL.

    Este mixin verifica automaticamente a propriedade do casamento
    antes de permitir qualquer operação, protegendo contra acessos
    não autorizados.

    Attributes:
        wedding: Instância do Wedding carregado da URL.
                Disponibilizado para uso nas views filhas.

    Usage:
        class SchedulerView(WeddingOwnershipMixin, TemplateView):
            # self.wedding estará disponível automaticamente
            def get_context_data(self, **kwargs):
                context = super().get_context_data(**kwargs)
                context['wedding'] = self.wedding
                return context

    Expects:
        - URL pattern deve ter 'wedding_id' como parâmetro
        - request.user deve estar autenticado
        - Wedding model deve ter campo 'planner'

    Raises:
        Http404: Se o casamento não existir.
        PermissionDenied: Se o usuário não for o planner do casamento.
    """

    wedding = None
    request: HttpRequest

    def dispatch(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """
        Intercepta a requisição para validar ownership do casamento.

        Args:
            request: Objeto HttpRequest do Django.
            *args: Argumentos posicionais.
            **kwargs: Argumentos nomeados (deve conter 'wedding_id').

        Returns:
            HttpResponse da view se autorizado.

        Raises:
            Http404: Se wedding_id não existir.
            PermissionDenied: Se não for o planner do casamento.
        """
        # Lazy import para evitar dependência circular
        from apps.weddings.models import Wedding

        # Busca o casamento pelo ID da URL
        wedding_id = self.kwargs.get("wedding_id")
        self.wedding = get_object_or_404(Wedding, id=wedding_id)

        # Verifica se o usuário é o planner do casamento
        if self.wedding.planner != request.user:
            raise PermissionDenied(
                "Você não tem permissão para acessar este casamento."
            )

        # Continua para o método (get, post) da view
        return super().dispatch(request, *args, **kwargs)  # type: ignore[misc]
