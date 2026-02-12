from rest_framework import serializers

from apps.core.serializers import BaseSerializer

from .models import Contract, Item, Supplier


class SupplierSerializer(BaseSerializer):
    """
    Serializer para o modelo Supplier.

    Mantém a paridade 1:1 com o SupplierDTO para permitir o
    mapeamento seguro via unpacking no ViewSet.
    """

    class Meta(BaseSerializer.Meta):
        model = Supplier
        # Estendemos os campos da BaseSerializer (uuid, created_at, updated_at)
        fields = [
            *BaseSerializer.Meta.fields,
            "name",
            "cnpj",
            "phone",
            "email",
            "website",
            "address",
            "city",
            "state",
            "notes",
            "is_active",
        ]
        # uuid e timestamps já estão como read_only na BaseSerializer


class ContractSerializer(BaseSerializer):
    """Serializer para contratos com suporte a upload de PDF."""

    class Meta(BaseSerializer.Meta):
        model = Contract
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "supplier",
            "total_amount",
            "description",
            "status",
            "expiration_date",
            "alert_days_before",
            "signed_date",
            "pdf_file",
        ]

    def validate_wedding(self, value):
        """Garante que o casamento pertence ao Planner logado."""
        if value.planner != self.context["request"].user:
            raise serializers.ValidationError(
                "Casamento inválido para este organizador."
            )
        return value


class ItemSerializer(BaseSerializer):
    """Serializer para itens de logística."""

    class Meta(BaseSerializer.Meta):
        model = Item
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "contract",
            "budget_category",
            "name",
            "description",
            "quantity",
            "acquisition_status",
        ]

    def validate(self, data):
        """Validação cruzada inicial (prevenindo erros óbvios)."""
        wedding = data.get("wedding")
        contract = data.get("contract")

        # Se houver contrato, ele deve pertencer ao mesmo casamento
        if contract and contract.wedding != wedding:
            raise serializers.ValidationError(
                {"contract": "O contrato selecionado não pertence a este casamento."}
            )
        return data
