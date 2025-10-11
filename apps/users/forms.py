from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

from apps.core.utils.django_forms import add_attr, add_placeholder
from apps.core.utils.mixins import FormStylingMixin

from .models import User


class CustomUserCreationForm(FormStylingMixin, UserCreationForm):
    email = forms.EmailField(label="E-mail")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields['username'], 'Digite seu usuário')
        add_placeholder(self.fields['email'], 'seu@email.com')
        add_placeholder(self.fields['first_name'], 'Seu primeiro nome')
        add_placeholder(self.fields['last_name'], 'Seu ultimo nome')
        add_placeholder(self.fields['password1'], 'Sua senha')
        add_placeholder(self.fields['password2'], 'Repita sua senha')

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
            ]

    username = forms.CharField(
        label="Usuário",
    )

    password1 = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(),
        help_text=(
            "Senha com pelo menos 8 caracteres, não totalmente "
            "numérica e pouco comum."
        ),
    )

    # password2 = forms.CharField(
    #     label="Confirme a senha",
    #     widget=forms.PasswordInput(),
    #     help_text='',
    # )


class SignInForm(FormStylingMixin, AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields['username'], 'Coloque seu usuário')
        add_placeholder(self.fields['password'], 'Coloque sua senha')

    username = forms.CharField(
        label="Nome de Usuário",
    )


class CustomUserChangeForm(UserChangeForm):
    password = None

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
