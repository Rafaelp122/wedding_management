from rest_framework import serializers

from apps.core.serializers import BaseSerializer
from apps.finances.models import BudgetCategory
from apps.weddings.models import Wedding

from .models import Contract, Item, Supplier


class SupplierSerializer(BaseSerializer):
    """Serializador para fornecedores, com campos básicos de contato e status."""

    class Meta(BaseSerializer.Meta):
        model = Supplier
        fields = [
            *BaseSerializer.Meta.fields,
            "name",
            "cnpj",
            "phone",
            "email",
            "is_active",
        ]


class ContractSerializer(BaseSerializer):
    """Serializador de contratos entre casamentos e fornecedores."""

    # DRF exige um queryset inicial se o campo não for read_only.
    # Usamos .all() e filtramos no __init__ para segurança.
    wedding = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Wedding.objects.all()
    )
    supplier = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Supplier.objects.all()
    )

    class Meta(BaseSerializer.Meta):
        model = Contract
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "supplier",
            "total_amount",
            "status",
        ]


class ItemSerializer(BaseSerializer):
    """Serializador de itens vinculados a casamentos, contratos e categorias
    de orçamento."""

    wedding = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Wedding.objects.all()
    )
    contract = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Contract.objects.all(),
        required=False,
        allow_null=True,
    )
    budget_category = serializers.SlugRelatedField(
        slug_field="uuid", queryset=BudgetCategory.objects.all()
    )

    class Meta(BaseSerializer.Meta):
        model = Item
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "contract",
            "budget_category",
            "name",
            "quantity",
        ]
