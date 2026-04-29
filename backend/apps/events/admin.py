from django.contrib import admin

from .models import Event, WeddingDetail


class WeddingDetailInline(admin.StackedInline):
    model = WeddingDetail
    can_delete = False
    verbose_name_plural = "Detalhes de Casamento"


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event_type",
        "company",
        "date",
        "location",
        "expected_guests",
        "status",
        "created_at",
    )
    list_filter = ("event_type", "status", "company", "date")
    search_fields = ("name", "location")
    inlines = [WeddingDetailInline]
