from urllib.parse import parse_qs, urlparse

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.exceptions import ImproperlyConfigured


class HtmxUrlParamsMixin:
    """
    GENÉRICO (Core): Fornece um helper para ler os query params
    do header 'HX-Current-Url' para preservar o estado.
    """

    def _get_params_from_htmx_url(self):
        """
        Lê a URL que o usuário estava vendo (do header HTMX).
        """
        current_url = self.request.headers.get("Hx-Current-Url")
        params = {}
        if current_url:
            try:
                # Parseia a URL para extrair os query params
                query_string = urlparse(current_url).query
                parsed_params = parse_qs(query_string)
                params = {k: v[0] for k, v in parsed_params.items()}
            except Exception:
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

    htmx_template_name = None
    htmx_retarget_id = None
    htmx_reswap_method = "innerHTML"

    def get_htmx_context_data(self, **kwargs):
        """
        Hook para adicionar contexto ao template HTMX.
        """
        kwargs["request"] = self.request
        return kwargs

    def render_htmx_response(self, trigger=None, **kwargs):
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
