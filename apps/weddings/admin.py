from django.contrib import admin

from .models import Wedding


@admin.register(Wedding)
class WeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "get_couple_names", "planner", "date", "location", "contract")
    list_filter = ("planner", "date")
    search_fields = ("location", "clients__name")

    def get_couple_names(self, obj):
        return " & ".join([c.name for c in obj.clients.all()])

    get_couple_names.short_description = "Couple"
