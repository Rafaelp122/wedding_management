import logging
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ImproperlyConfigured
from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


class HtmxUrlParamsMixin:
    """
    GENÉRICO (Core): Fornece um helper para ler os query params
    do header 'HX-Current-Url' para preservar o estado.

    Este mixin é útil em views HTMX que precisam manter o contexto
    de paginação, filtros ou ordenação ao processar requisições AJAX.

    O header HX-Current-Url contém a URL completa que o usuário
    estava visualizando quando fez a requisição HTMX.

    Usage:
        class MyHtmxView(HtmxUrlParamsMixin, View):
            def get(self, request):
                params = self._get_params_from_htmx_url()
                page = params.get('page', '1')
                # ... processar com os parâmetros preservados
    """

    request: HttpRequest

    def _get_params_from_htmx_url(self) -> Dict[str, str]:
        """
        Extrai os query parameters do header HX-Current-Url.

        Lê a URL que o usuário estava vendo (do header HTMX)
        e extrai todos os parâmetros da query string.

        Returns:
            Dicionário com os parâmetros extraídos.
            Se houver parâmetros duplicados, retorna apenas o primeiro.
            Retorna dict vazio se não houver header ou em caso de erro.

        Note:
            Em caso de erro no parsing, não quebra a requisição,
            apenas loga o aviso e retorna dict vazio.
        """
        current_url = self.request.headers.get("Hx-Current-Url")
        params: Dict[str, str] = {}

        if current_url:
            try:
                # Parseia a URL para extrair os query params
                query_string = urlparse(current_url).query
                parsed_params = parse_qs(
                    query_string, keep_blank_values=True
                )
                # parse_qs retorna listas, pegamos apenas o primeiro
                params = {k: v[0] for k, v in parsed_params.items()}
            except Exception as e:
                # Não quebra a requisição, mas avisa no log
                logger.warning(
                    f"Falha ao parsear HX-Current-Url: {current_url}. "
                    f"Erro: {e}",
                    exc_info=True,
                )
        return params


class BaseHtmxResponseMixin:
    """
    GENÉRICO (Core): Fornece um método helper para
    renderizar respostas HTMX genéricas.

    Este mixin facilita a criação de respostas HTMX,
    automatizando a renderização de templates e a configuração
    dos headers necessários (HX-Retarget, HX-Reswap, HX-Trigger).

    Attributes:
        htmx_template_name: Nome do template a ser renderizado
                           para respostas HTMX.
        htmx_retarget_id: Seletor CSS do elemento alvo
                         (ex: '#item-list', '.results').
        htmx_reswap_method: Método de substituição HTMX
                           (innerHTML, outerHTML, beforeend, etc).
                           Padrão: 'innerHTML'.

    Usage:
        class MyHtmxView(BaseHtmxResponseMixin, View):
            htmx_template_name = 'partials/items.html'
            htmx_retarget_id = '#items-container'

            def get(self, request):
                items = Item.objects.all()
                return self.render_htmx_response(items=items)

    A view/mixin que herda DEVE fornecer:
    - self.request: HttpRequest (herdado da View)
    - self.htmx_template_name (str): Nome do template
    - self.htmx_retarget_id (str): ID/seletor do elemento alvo
    """

    htmx_template_name: Optional[str] = None
    htmx_retarget_id: Optional[str] = None
    htmx_reswap_method: str = "innerHTML"

    request: HttpRequest

    def get_htmx_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Hook para adicionar contexto ao template HTMX.

        Args:
            **kwargs: Dados de contexto adicionais para o template.

        Returns:
            Dicionário com o contexto fornecido + request injetado.

        Note:
            Injeta 'request' automaticamente para facilitar uso no template.
        """
        kwargs["request"] = self.request
        return kwargs

    def render_htmx_response(
        self, trigger: Optional[str] = None, **kwargs: Any
    ) -> HttpResponse:
        """
        Renderiza uma resposta HTMX com os headers apropriados.

        Este método renderiza o template especificado e configura
        automaticamente os headers HTMX necessários para atualizar
        a página corretamente.

        Args:
            trigger: Nome do evento HTMX a ser disparado após o swap
                    (ex: 'itemUpdated', 'listRefreshed').
                    Opcional.
            **kwargs: Dados de contexto para o template.

        Returns:
            HttpResponse com o HTML renderizado e headers HTMX
            configurados.

        Raises:
            ImproperlyConfigured: Se htmx_template_name ou
                                 htmx_retarget_id não estiverem
                                 definidos.

        Example:
            return self.render_htmx_response(
                trigger='itemAdded',
                items=items,
                total=count
            )
        """
        if not self.htmx_template_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define "
                "'htmx_template_name'."
            )

        if not self.htmx_retarget_id:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define "
                "'htmx_retarget_id'."
            )

        context = self.get_htmx_context_data(**kwargs)

        # Renderiza o template com o contexto
        html = render_to_string(
            self.htmx_template_name,
            context,
            request=self.request,
        )

        # Cria a resposta HTTP
        response = HttpResponse(html)

        # Configura headers HTMX
        response["HX-Retarget"] = self.htmx_retarget_id
        response["HX-Reswap"] = self.htmx_reswap_method

        # Adiciona trigger se especificado
        if trigger:
            response["HX-Trigger-After-Swap"] = trigger

        return response


class ModalContextMixin:
    """
    Mixin genérico para contexto de modais de formulário.

    Este mixin extrai a lógica comum de construção de contexto
    para modais, evitando duplicação entre Create/Update views.

    Fornece métodos para obter título do modal, texto do botão
    e URL de POST, que devem ser definidos como atributos ou
    implementados pelas views concretas.

    Attributes:
        modal_title: Título do modal.
        submit_button_text: Texto do botão de submit.

    Usage:
        class MyCreateView(ModalContextMixin, CreateView):
            modal_title = "Criar Item"
            submit_button_text = "Salvar"

            def get_hx_post_url(self) -> str:
                return reverse('items:create')
    """

    modal_title: str = ""
    submit_button_text: str = ""

    def get_modal_title(self) -> str:
        """Retorna o título do modal."""
        return self.modal_title

    def get_submit_button_text(self) -> str:
        """Retorna o texto do botão de submit."""
        return self.submit_button_text

    def get_hx_post_url(self) -> str:
        """
        Retorna a URL para o POST do formulário.

        Deve ser implementado pela view concreta.

        Raises:
            NotImplementedError: Se não for implementado pela subclasse.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_hx_post_url()"
        )

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Adiciona contexto do modal ao contexto do template.

        Args:
            **kwargs: Argumentos de contexto adicionais.

        Returns:
            Dicionário com o contexto completo incluindo dados do modal.
        """
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        context["modal_title"] = self.get_modal_title()
        context["submit_button_text"] = self.get_submit_button_text()
        context["hx_post_url"] = self.get_hx_post_url()
        return context
