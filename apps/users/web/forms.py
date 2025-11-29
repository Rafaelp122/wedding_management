"""
Formulários customizados para autenticação e perfil de usuário.

Os formulários de signup e login herdam do django-allauth e aplicam
nosso FormStylingMixin para manter a consistência visual.
"""

import logging
from typing import ClassVar

from allauth.account.forms import LoginForm, ResetPasswordForm, SignupForm
from django import forms
from django.contrib.auth.forms import UserChangeForm

from apps.core.mixins.forms import FormStylingMixin, FormStylingMixinLarge
from apps.core.utils.forms_utils import add_placeholder

from ..models import User

logger = logging.getLogger(__name__)


class CustomUserCreationForm(FormStylingMixinLarge, SignupForm):
    """
    Formulário de registro de novos usuários adaptado para django-allauth.
    Herda de FormStylingMixinLarge para inputs maiores e mais amigáveis.
    """

    # Adicionamos first_name e last_name que não são padrão do SignupForm
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label="Primeiro Nome",
        widget=forms.TextInput(attrs={"placeholder": "Ex: Pedro"}),
    )
    last_name = forms.CharField(
        max_length=150,
        required=False,
        label="Último Nome",
        widget=forms.TextInput(attrs={"placeholder": "Ex: Silva"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizando labels e placeholders dos campos do allauth
        self.fields["username"].label = "Usuário"
        self.fields["email"].label = "E-mail"
        self.fields["password1"].label = "Senha"
        self.fields[
            "password1"
        ].help_text = (
            "Senha com pelo menos 8 caracteres, não totalmente numérica e pouco comum."
        )
        self.fields["password2"].label = "Confirme a senha"

        # Placeholders
        # add_placeholder(self.fields["username"], "Digite seu usuário")
        # add_placeholder(self.fields["email"], "seu@email.com")
        # add_placeholder(self.fields["password1"], "Sua senha")
        # add_placeholder(self.fields["password2"], "Repita sua senha")

    def save(self, request):
        """
        Salva o usuário incluindo first_name e last_name.
        O método save do allauth já lida com a criação do usuário.
        """
        user = super().save(request)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.last_name = self.cleaned_data.get("last_name", "")
        user.save()
        return user

    def clean(self):
        """Loga tentativas falhas de registro."""
        cleaned_data = super().clean()
        if self.errors:
            logger.warning(f"Falha no registro de usuário: {self.errors.keys()}")
        return cleaned_data


class CustomLoginForm(FormStylingMixinLarge, LoginForm):
    """
    Formulário de login customizado do django-allauth.
    Herda de FormStylingMixinLarge para inputs maiores e mais amigáveis.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizando labels e placeholders dos campos do allauth
        self.fields["login"].label = "Usuário ou E-mail"
        self.fields["password"].label = "Senha"

        if "remember" in self.fields:
            self.fields["remember"].label = "Lembrar de mim"
            # Aplica classe de checkbox do Bootstrap
            self.fields["remember"].widget.attrs.update({"class": "form-check-input"})

        # Placeholders
        # add_placeholder(self.fields["login"], "Digite seu usuário ou e-mail")
        # add_placeholder(self.fields["password"], "Sua senha")


class CustomResetPasswordForm(FormStylingMixinLarge, ResetPasswordForm):
    """
    Formulário de recuperação de senha customizado do django-allauth.
    Herda de FormStylingMixinLarge para inputs maiores e mais amigáveis.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Personalizando labels do campo email
        self.fields["email"].label = "E-mail"

        # Placeholders
        # add_placeholder(self.fields["email"], "seu@email.com")


class CustomUserChangeForm(FormStylingMixin, UserChangeForm):
    """
    Formulário para edição de perfil (nome, email).
    A senha é removida para evitar alterações acidentais aqui.
    """

    password = None

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels: ClassVar[dict] = {
            "username": "Usuário",
            "first_name": "Primeiro Nome",
            "last_name": "Último Nome",
            "email": "E-mail",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["username"], "Digite seu usuário")
        add_placeholder(self.fields["email"], "seu@email.com")
        add_placeholder(self.fields["first_name"], "Ex: Pedro")
        add_placeholder(self.fields["last_name"], "Ex: Silva")
