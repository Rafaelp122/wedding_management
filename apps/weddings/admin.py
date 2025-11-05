from django.contrib import admin
from .models import Wedding


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "display_couple_or_client", "planner", "date", "location")
    list_filter = ("planner", "date")
    search_fields = ("location", "client__name", "groom_name", "bride_name")

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
