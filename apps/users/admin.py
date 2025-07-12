from django.contrib import admin

from .models import Planner


@admin.register(Planner)
class PlannerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'cpf_cnpj', 'phone')
    search_fields = ('name', 'email', 'cpf_cnpj')
