import logging

from django import forms
from django.contrib.auth.forms import (AuthenticationForm, UserChangeForm,
                                       UserCreationForm)

from apps.core.mixins.forms import FormStylingMixin, FormStylingMixinLarge
from apps.core.utils.forms_utils import add_placeholder

from ..models import User

logger = logging.getLogger(__name__)


class CustomUserCreationForm(FormStylingMixinLarge, UserCreationForm):
    """
    Formulário de registro de novos usuários.
    Herda de FormStylingMixinLarge para inputs maiores e mais amigáveis.
    """

    # Forçamos o campo email a ser obrigatório e do tipo EmailField
    email = forms.EmailField(label="E-mail", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name")
        # Definir labels aqui limpa o __init__
        labels = {
            "username": "Usuário",
            "first_name": "Primeiro Nome",
            "last_name": "Último Nome",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Campos de senha não estão no Meta (são do Form), definimos aqui
        self.fields["password1"].label = "Senha"
        self.fields["password1"].help_text = (
            "Senha com pelo menos 8 caracteres, não totalmente "
            "numérica e pouco comum."
        )
        self.fields["password2"].label = "Confirme a senha"

        # Placeholders
        add_placeholder(self.fields["username"], "Digite seu usuário")
        add_placeholder(self.fields["email"], "seu@email.com")
        add_placeholder(self.fields["first_name"], "Ex: Pedro")
        add_placeholder(self.fields["last_name"], "Ex: Silva")
        add_placeholder(self.fields["password1"], "Sua senha")
        add_placeholder(self.fields["password2"], "Repita sua senha")

    def clean(self):
        """Loga tentativas falhas de registro."""
        cleaned_data = super().clean()
        if self.errors:
            logger.warning(f"Falha no registro de usuário: {self.errors.keys()}")
        return cleaned_data


class SignInForm(FormStylingMixinLarge, AuthenticationForm):
    """
    Formulário de Login.
    Nota: AuthenticationForm valida se o usuário existe e a senha bate.
    """
    username = forms.CharField(label="Nome de Usuário")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_placeholder(self.fields["username"], "Seu usuário")
        add_placeholder(self.fields["password"], "Sua senha")

    def clean(self):
        """Loga tentativas falhas de login."""
        try:
            # O AuthenticationForm lança ValidationError se o login falhar
            cleaned_data = super().clean()
            return cleaned_data
        except forms.ValidationError as e:
            # Capturamos o erro, logamos e re-lançamos o erro para o Django tratar
            username = self.cleaned_data.get("username", "unknown")
            logger.warning(f"Tentativa de login falhou para o usuário: '{username}'")
            raise e


class CustomUserChangeForm(FormStylingMixin, UserChangeForm):
    """
    Formulário para edição de perfil (nome, email).
    A senha é removida para evitar alterações acidentais aqui.
    """
    password = None

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
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
