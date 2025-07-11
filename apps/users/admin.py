from django.contrib import admin

from .models import Cerimonialista


@admin.register(Cerimonialista)
class CerimonialistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf_cnpj', 'telefone')
    search_fields = ('nome', 'email', 'cpf_cnpj')
