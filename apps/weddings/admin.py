from django.contrib import admin
from .models import Wedding
from apps.budget.models import Budget


class BudgetInline(admin.StackedInline):
    model = Budget
    extra = 1  # Mostra um formulário de orçamento por padrão na criação.
    max_num = 1  # Não permite adicionar mais de um.
    can_delete = False  # Evita apagar o orçamento acidentalmente.


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "display_couple_or_client", "planner", "date", "location")
    list_filter = ("planner", "date")
    search_fields = ("location", "client__name", "groom_name", "bride_name")

    inlines = [BudgetInline]

    def display_couple_or_client(self, obj):
        # Se os nomes dos noivos foram preenchidos, use-os.
        if obj.groom_name and obj.bride_name:
            return f"{obj.groom_name} & {obj.bride_name}"
        # Senão, use o nome do cliente associado.
        if obj.client:
            return obj.client.name
        return "Cliente não definido"  # Caso nenhum esteja disponível

    # Define o título da coluna na tabela do admin.
    display_couple_or_client.short_description = "Casal / Cliente"
