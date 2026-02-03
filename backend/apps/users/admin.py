"""Configuração do Django Admin para o modelo User customizado.

Define a interface administrativa para gerenciamento de usuários,
incluindo visualizações, filtros, campos de edição e permissões.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin customizado para o modelo User.

    Adapta o UserAdmin padrão do Django para trabalhar com o modelo User
    que usa email como identificador único.

    Features:
        - Lista usuários com email, nome, status de equipe e status ativo
        - Filtros por tipo de usuário (staff, superuser, ativo)
        - Busca por email e nome
        - Organização de campos em seções lógicas
        - Interface horizontal para grupos e permissões
        - Campos de data somente leitura para auditoria
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ("email", "name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "name")
    ordering = ("-date_joined",)

    # REMOVE 'password' do fieldsets. O UserChangeForm injeta o link de troca
    # de senha automaticamente.
    fieldsets = (
        ("Informações Pessoais", {"fields": ("name", "email")}),
        (
            "Permissões",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Datas", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name",
                    "password1",
                    "password2",
                ),  # O form cuida disso
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")
