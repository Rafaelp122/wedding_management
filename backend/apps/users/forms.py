"""Formulários customizados para o modelo User.

Define formulários de criação e edição de usuários adaptados
para usar email como identificador e incluir o campo name.
"""

from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserChangeForm(UserChangeForm):
    """Formulário de edição de usuário existente.

    Herda de UserChangeForm do Django e adapta para o modelo User customizado.
    Inclui automaticamente o link para alteração de senha no Django Admin.
    """

    class Meta:
        model = User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    """Formulário de criação de novo usuário.

    Herda de UserCreationForm do Django e adapta para o modelo User customizado.
    Define email e name como campos iniciais obrigatórios, além da senha.
    """

    class Meta:
        model = User
        fields = ("email", "name")  # Campos iniciais obrigatórios
