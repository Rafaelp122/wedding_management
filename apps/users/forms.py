from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)

from apps.core.utils.django_forms import add_attr

from .models import User


def add_placeholder(field, placeholder_val):
    add_attr(field, 'placeholder', placeholder_val)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(label="E-mail")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, 'class', 'form-check-input')
            else:
                add_attr(field, 'class', 'form-control')

            if field_name in self.errors:
                add_attr(field, 'class', 'is-invalid')

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


class SignInForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, 'class', 'form-check-input')
            else:
                add_attr(field, 'class', 'form-control')

            if field_name in self.errors:
                add_attr(field, 'class', 'is-invalid')

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
