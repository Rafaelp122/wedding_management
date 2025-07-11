from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Cerimonialista, Cliente, Fornecedor

@admin.register(Cerimonialista)
class CerimonialistaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf_cnpj', 'telefone')
    search_fields = ('nome', 'email', 'cpf_cnpj')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf', 'telefone')
    search_fields = ('nome', 'email', 'cpf')

@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'cpf_cnpj', 'telefone', 'servicos_oferecidos')
    search_fields = ('nome', 'email', 'cpf_cnpj')
