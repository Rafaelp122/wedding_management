"""
Core Mixins - Componentes reutilizáveis para views e forms.

Este módulo exporta mixins genéricos que podem ser usados em
toda a aplicação para adicionar funcionalidades comuns.

Auth Mixins:
    - OwnerRequiredMixin: Garante acesso apenas ao proprietário
    - RedirectAuthenticatedUserMixin: Redireciona usuários logados

Form Mixins:
    - FormStylingMixin: Aplica classes CSS Bootstrap (tamanho normal)
    - FormStylingMixinLarge: Aplica classes CSS Bootstrap (tamanho grande)
    - BaseFormStylingMixin: Classe base para customização

View Mixins:
    - HtmxUrlParamsMixin: Extrai parâmetros do header HX-Current-Url
    - BaseHtmxResponseMixin: Renderiza respostas HTMX padronizadas
"""

# Auth Mixins
from .auth import OwnerRequiredMixin, RedirectAuthenticatedUserMixin

# Form Mixins
from .forms import BaseFormStylingMixin, FormStylingMixin, FormStylingMixinLarge

# View Mixins
from .views import BaseHtmxResponseMixin, HtmxUrlParamsMixin

__all__ = [
    # Auth
    "OwnerRequiredMixin",
    "RedirectAuthenticatedUserMixin",
    # Forms
    "BaseFormStylingMixin",
    "FormStylingMixin",
    "FormStylingMixinLarge",
    # Views
    "BaseHtmxResponseMixin",
    "HtmxUrlParamsMixin",
]
