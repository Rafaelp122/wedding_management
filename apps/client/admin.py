from django.contrib import admin
from .models import Client


# Configuração de exibição do modelo Client no painel admin
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "cpf", "phone")  # Campos mostrados na lista
    search_fields = ("name", "email", "cpf")  # Campos pesquisáveis no admin
