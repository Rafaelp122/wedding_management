"""Configuração do Django Admin para o modelo User customizado.

Define a interface administrativa para gerenciamento de usuários,
incluindo visualizações, filtros, campos de edição e permissões,
agora utilizando campos explícitos para primeiro nome e sobrenome.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    """Admin customizado para o modelo User.

    Adapta o UserAdmin padrão do Django para trabalhar com o modelo User
    que usa email como identificador único e separação de nomes.

    Features:
        - Lista usuários com email, primeiro nome, sobrenome e status
        - Filtros por tipo de usuário (staff, superuser, ativo)
        - Busca por email, primeiro nome e sobrenome
        - Organização de campos em seções lógicas (Informações Pessoais)
        - Interface horizontal para grupos e permissões
        - Campos de data somente leitura para auditoria
    """

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    # Exibição na listagem principal
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-date_joined",)

    # Configuração do formulário de EDIÇÃO
    fieldsets = (
        ("Informações Pessoais", {"fields": ("first_name", "last_name", "email")}),
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
        ("Datas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Configuração do formulário de CRIAÇÃO (Novo Usuário)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password",  # O BaseUserAdmin ou seu form lida com a confirmação
                ),
            },
        ),
    )

    readonly_fields = ("last_login", "date_joined")
    filter_horizontal = ("groups", "user_permissions")
