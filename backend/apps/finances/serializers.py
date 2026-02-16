from rest_framework import serializers

from apps.core.serializers import BaseSerializer
from apps.logistics.models import Contract
from apps.weddings.models import Wedding

from .models import Budget, BudgetCategory, Expense, Installment


class BudgetSerializer(BaseSerializer):
    """
    Serializer para o Orçamento Mestre.
    """

    wedding = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Wedding.objects.all(),
        help_text="UUID do Casamento vinculado",
    )

    class Meta(BaseSerializer.Meta):
        model = Budget
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "total_estimated",
            "notes",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            # Refinamento do multitenancy em tempo de execução
            self.fields["wedding"].queryset = Wedding.objects.filter(planner=user)


class BudgetCategorySerializer(BaseSerializer):
    """
    Serializer para Categorias de Orçamento.
    """

    wedding = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Wedding.objects.all()
    )
    budget = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Budget.objects.all()
    )

    class Meta(BaseSerializer.Meta):
        model = BudgetCategory
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "budget",
            "name",
            "description",
            "allocated_budget",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            self.fields["wedding"].queryset = Wedding.objects.filter(planner=user)
            self.fields["budget"].queryset = Budget.objects.filter(
                wedding__planner=user
            )


class ExpenseSerializer(BaseSerializer):
    """
    Serializer para Despesas.
    """

    category = serializers.SlugRelatedField(
        slug_field="uuid", queryset=BudgetCategory.objects.all()
    )
    contract = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Contract.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta(BaseSerializer.Meta):
        model = Expense
        fields = [
            *BaseSerializer.Meta.fields,
            "category",
            "contract",
            "description",
            "estimated_amount",
            "actual_amount",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            self.fields["category"].queryset = BudgetCategory.objects.filter(
                wedding__planner=user
            )
            self.fields["contract"].queryset = Contract.objects.filter(
                wedding__planner=user
            )


class InstallmentSerializer(BaseSerializer):
    """
    Serializer para Parcelas.
    """

    expense = serializers.SlugRelatedField(
        slug_field="uuid", queryset=Expense.objects.all()
    )

    class Meta(BaseSerializer.Meta):
        model = Installment
        fields = [
            *BaseSerializer.Meta.fields,
            "expense",
            "installment_number",
            "amount",
            "due_date",
            "paid_date",
            "status",
            "notes",
        ]
        read_only_fields = [*BaseSerializer.Meta.read_only_fields, "status"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "request" in self.context:
            user = self.context["request"].user
            self.fields["expense"].queryset = Expense.objects.filter(
                wedding__planner=user
            )
