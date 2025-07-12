from django.contrib import admin

from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'cpf', 'phone')
    search_fields = ('name', 'email', 'cpf')
