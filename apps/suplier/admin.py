from django.contrib import admin

from .models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'email',
        'cpf_cnpj',
        'telefone',
        'servicos_oferecidos',
    )
    search_fields = (
        'nome',
        'email',
        'cpf_cnpj',
    )
