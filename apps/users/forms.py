from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

from apps.core.utils.django_forms import add_placeholder
from apps.core.utils.mixins import FormStylingMixin, FormStylingMixinLarge

from .models import User


class CustomUserCreationForm(FormStylingMixinLarge, UserCreationForm):
    # Apenas campos NOVOS são declarados aqui
    email = forms.EmailField(
        label="E-mail",
        # help_text="O e-mail é obrigatório."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Adicione os campos que você quer do UserCreationForm + o seu novo campo 'email'
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Usuário"
        self.fields["first_name"].label = "Primeiro Nome"
        self.fields["last_name"].label = "Último Nome"

        self.fields["password1"].label = "Senha"
        self.fields["password1"].help_text = (
            "Senha com pelo menos 8 caracteres, não totalmente "
            "numérica e pouco comum."
        )
        self.fields["password2"].label = "Confirme a senha"

        add_placeholder(self.fields["username"], "Digite seu usuário")
        add_placeholder(self.fields["email"], "seu@email.com")
        add_placeholder(self.fields["first_name"], "Ex: Pedro")
        add_placeholder(self.fields["last_name"], "Ex: Silva")
        add_placeholder(self.fields["password1"], "Sua senha")
        add_placeholder(self.fields["password2"], "Repita sua senha")


class SignInForm(FormStylingMixinLarge, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["username"], "Seu usuário")
        add_placeholder(self.fields["password"], "Sua senha")

    username = forms.CharField(
        label="Nome de Usuário",
    )


class CustomUserChangeForm(FormStylingMixin, UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Usuário"
        self.fields["first_name"].label = "Primeiro Nome"
        self.fields["last_name"].label = "Último Nome"
        self.fields["email"].label = "E-mail"

        add_placeholder(self.fields["username"], "Digite seu usuário")
        add_placeholder(self.fields["email"], "seu@email.com")
        add_placeholder(self.fields["first_name"], "Ex: Pedro")
        add_placeholder(self.fields["last_name"], "Ex: Silva")
