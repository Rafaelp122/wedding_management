"""
Adapters customizados para django-allauth.

Permite customizar o comportamento das views do allauth,
como adicionar contexto extra (ícones, layout) para os templates.
"""

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Adapter customizado para adicionar contexto aos templates do allauth.
    """

    def get_signup_form_initial_data(self, request):
        """Dados iniciais do formulário de signup."""
        return {}

    def add_message(
        self,
        request,
        level,
        message_template,
        message_context=None,
        extra_tags="",
    ):
        """
        Customiza as mensagens do allauth.
        Por padrão, apenas chama o comportamento padrão.
        """
        return super().add_message(
            request, level, message_template, message_context, extra_tags
        )
