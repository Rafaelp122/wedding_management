from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'email',
        'cpf_cnpj',
        'phone',
        'offered_services',
    )
    search_fields = (
        'name',
        'email',
        'cpf_cnpj',
    )
