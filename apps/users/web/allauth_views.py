"""
Views customizadas do django-allauth.

Sobrescreve as views padrão do allauth para adicionar contexto
customizado (ícones, layout) aos templates.
"""

from allauth.account.views import (LoginView, LogoutView, PasswordResetView,
                                   SignupView)
from django.urls import reverse_lazy


class CustomSignupView(SignupView):
    """View customizada de signup que adiciona ícones e layout."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Layout das colunas dos campos
        context["form_layout_dict"] = {
            "username": "col-md-6",
            "first_name": "col-md-6",
            "last_name": "col-md-6",
            "email": "col-md-6",
            "password1": "col-md-6",
            "password2": "col-md-6",
        }

        # Ícones dos campos
        context["form_icons"] = {
            "username": "fas fa-user",
            "email": "fas fa-envelope",
            "first_name": "fas fa-id-card",
            "last_name": "fas fa-id-card",
            "password1": "fas fa-lock",
            "password2": "fas fa-lock",
        }

        context["form_action"] = reverse_lazy("account_signup")
        context["button_text"] = "Cadastrar"
        context["default_col_class"] = "col-md-6"

        return context


class CustomLoginView(LoginView):
    """View customizada de login que adiciona ícones e layout."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Layout das colunas dos campos
        context["form_layout_dict"] = {
            "login": "col-md-12",
            "password": "col-md-12",
            "remember": "col-md-12",  # Checkbox "Lembrar de mim"
        }

        # Ícones dos campos (checkbox não precisa de ícone)
        context["form_icons"] = {
            "login": "fas fa-user",
            "password": "fas fa-lock",
        }

        context["form_action"] = reverse_lazy("account_login")
        context["button_text"] = "Entrar"
        context["default_col_class"] = "col-md-12"

        return context


class CustomLogoutView(LogoutView):
    """View customizada de logout."""

    pass


class CustomPasswordResetView(PasswordResetView):
    """View customizada de recuperação de senha."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Layout das colunas dos campos
        context["form_layout_dict"] = {
            "email": "col-md-12",
        }

        # Ícones dos campos
        context["form_icons"] = {
            "email": "fas fa-envelope",
        }

        context["button_text"] = "Enviar Instruções"
        context["default_col_class"] = "col-md-12"

        return context
