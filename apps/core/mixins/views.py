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
    """

    request: HttpRequest

    def _get_params_from_htmx_url(self) -> Dict[str, str]:
        """
        Lê a URL que o usuário estava vendo (do header HTMX).
        """
        current_url = self.request.headers.get("Hx-Current-Url")
        params: Dict[str, str] = {}
        if current_url:
            try:
                # Parseia a URL para extrair os query params
                query_string = urlparse(current_url).query
                parsed_params = parse_qs(query_string, keep_blank_values=True)
                params = {k: v[0] for k, v in parsed_params.items()}
            except Exception as e:
                # não quebra a requisição, mas avisa o desenvolvedor no log.
                logger.warning(
                    f"Falha ao parsear HX-Current-Url: {current_url}. Erro: {e}",
                    exc_info=True,
                )
                pass  # Se falhar, usa os defaults (page=1, etc)
        return params


class BaseHtmxResponseMixin:
    """
    GENÉRICO (Core): Fornece um método helper para
    renderizar respostas HTMX genéricas.

    A view/mixin que herda DEVE fornecer:
    - self.request
    - self.htmx_template_name (str)
    - self.htmx_retarget_id (str)
    """

    htmx_template_name: Optional[str] = None
    htmx_retarget_id: Optional[str] = None

    htmx_reswap_method: str = "innerHTML"
    request: HttpRequest

    def get_htmx_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Hook para adicionar contexto ao template HTMX.
        """
        kwargs["request"] = self.request
        return kwargs

    def render_htmx_response(
        self, trigger: Optional[str] = None, **kwargs: Any
    ) -> HttpResponse:
        """
        Método genérico: Renderiza o template e anexa
        os headers HTMX.
        """
        if not self.htmx_template_name:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define 'htmx_template_name'."
            )

        if not self.htmx_retarget_id:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} must define 'htmx_retarget_id'."
            )

        context = self.get_htmx_context_data(**kwargs)

        # Usamos direto o self.htmx_template_name, pois já validamos acima
        html = render_to_string(
            self.htmx_template_name,
            context,
            request=self.request,
        )

        response = HttpResponse(html)
        response["HX-Retarget"] = self.htmx_retarget_id
        response["HX-Reswap"] = self.htmx_reswap_method

        if trigger:
            response["HX-Trigger-After-Swap"] = trigger

        return response
