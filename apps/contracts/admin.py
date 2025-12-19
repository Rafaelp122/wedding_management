from django.contrib import admin
from django.utils.html import format_html

from .models import Contract


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    """Configuração administrativa para o modelo Contract."""

    list_display = (
        "id",
        "item_name",
        "wedding_couple",
        "supplier_name",
        "status",
        "contract_value",
        "signature_progress",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
        "planner_signed_at",
        "supplier_signed_at",
        "couple_signed_at",
    )

    search_fields = (
        "item__name",
        "item__supplier",
        "item__wedding__groom_name",
        "item__wedding__bride_name",
        "token",
    )

    readonly_fields = (
        "token",
        "integrity_hash",
        "planner_signed_at",
        "planner_ip",
        "supplier_signed_at",
        "supplier_ip",
        "couple_signed_at",
        "couple_ip",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        ("Informações Básicas", {"fields": ("item", "description", "status", "token")}),
        (
            "Assinatura do Cerimonialista",
            {"fields": ("planner_signature", "planner_signed_at", "planner_ip")},
        ),
        (
            "Assinatura do Fornecedor",
            {"fields": ("supplier_signature", "supplier_signed_at", "supplier_ip")},
        ),
        (
            "Assinatura dos Noivos",
            {"fields": ("couple_signature", "couple_signed_at", "couple_ip")},
        ),
        ("Integridade e Arquivos", {"fields": ("integrity_hash", "final_pdf")}),
        (
            "Metadados",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def item_name(self, obj):
        """Retorna o nome do item vinculado."""
        return obj.item.name if obj.item else "-"

    item_name.short_description = "Item/Serviço"

    def wedding_couple(self, obj):
        """Retorna os nomes dos noivos."""
        if obj.wedding:
            return f"{obj.wedding.bride_name} & {obj.wedding.groom_name}"
        return "-"

    wedding_couple.short_description = "Noivos"

    def supplier_name(self, obj):
        """Retorna o nome do fornecedor."""
        return obj.supplier or "-"

    supplier_name.short_description = "Fornecedor"

    def contract_value(self, obj):
        """Retorna o valor total do contrato."""
        return f"R$ {obj.contract_value:,.2f}"

    contract_value.short_description = "Valor"

    def signature_progress(self, obj):
        """Mostra visualmente o progresso das assinaturas."""
        signatures = []

        if obj.planner_signature:
            signatures.append('<span style="color: green;">✓ Cerimonialista</span>')
        else:
            signatures.append('<span style="color: gray;">○ Cerimonialista</span>')

        if obj.supplier_signature:
            signatures.append('<span style="color: green;">✓ Fornecedor</span>')
        else:
            signatures.append('<span style="color: gray;">○ Fornecedor</span>')

        if obj.couple_signature:
            signatures.append('<span style="color: green;">✓ Noivos</span>')
        else:
            signatures.append('<span style="color: gray;">○ Noivos</span>')

        return format_html("{}", " | ".join(signatures))

    signature_progress.short_description = "Assinaturas"
