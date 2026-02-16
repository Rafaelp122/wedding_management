from rest_framework import serializers

from apps.core.serializers import BaseSerializer
from apps.finances.models import BudgetCategory
from apps.weddings.models import Wedding

from .models import Contract, Item, Supplier


class SupplierSerializer(BaseSerializer):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            self.fields["wedding"].queryset = Wedding.objects.filter(planner=user)
            self.fields["supplier"].queryset = Supplier.objects.filter(planner=user)


class ItemSerializer(BaseSerializer):
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            self.fields["wedding"].queryset = Wedding.objects.filter(planner=user)
            self.fields["contract"].queryset = Contract.objects.filter(
                wedding__planner=user
            )
            self.fields["budget_category"].queryset = BudgetCategory.objects.filter(
                wedding__planner=user
            )
