from django.contrib import admin
from .models import Wedding


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "display_couple", "planner", "date", "location")
    list_filter = ("planner", "date")
    search_fields = ("location", "groom_name", "bride_name")

    def display_couple(self, obj):
        # Se os nomes dos noivos foram preenchidos, use-os.
        return f"{obj.groom_name} & {obj.bride_name}"

    # Define o título da coluna na tabela do admin.
    display_couple.short_description = "Casal"
