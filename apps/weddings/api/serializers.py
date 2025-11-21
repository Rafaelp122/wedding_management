"""
Serializers para a API REST de Wedding.
"""

from rest_framework import serializers

from apps.weddings.models import Wedding


class WeddingListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de casamentos.

    Usado no endpoint GET /api/v1/weddings/
    Retorna apenas informações essenciais para performance.
    """

    planner_name = serializers.CharField(source="planner.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    couple_name = serializers.SerializerMethodField()

    class Meta:
        model = Wedding
        fields = [
            "id",
            "couple_name",
            "groom_name",
            "bride_name",
            "date",
            "location",
            "status",
            "status_display",
            "planner_name",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_couple_name(self, obj):
        """Retorna o nome do casal formatado."""
        return f"{obj.groom_name} & {obj.bride_name}"


class WeddingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de um casamento específico.

    Usado no endpoint GET /api/v1/weddings/{id}/
    Inclui informações detalhadas e relacionamentos.
    """

    planner_name = serializers.CharField(source="planner.get_full_name", read_only=True)
    planner_email = serializers.EmailField(source="planner.email", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    couple_name = serializers.SerializerMethodField()

    # Contadores (assumindo que você tem related_names definidos)
    items_count = serializers.SerializerMethodField()
    contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Wedding
        fields = [
            "id",
            "couple_name",
            "groom_name",
            "bride_name",
            "date",
            "location",
            "budget",
            "status",
            "status_display",
            "planner_name",
            "planner_email",
            "items_count",
            "contracts_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_couple_name(self, obj):
        """Retorna o nome do casal formatado."""
        return f"{obj.groom_name} & {obj.bride_name}"

    def get_items_count(self, obj):
        """Retorna o número de itens associados ao casamento."""
        return obj.items.count() if hasattr(obj, 'items') else 0

    def get_contracts_count(self, obj):
        """Retorna o número de contratos associados ao casamento."""
        # Assuming contracts are related through items
        return sum(item.contracts.count() for item in obj.items.all()) if hasattr(obj, 'items') else 0


class WeddingSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de casamentos.

    Usado nos endpoints:
    - POST /api/v1/weddings/
    - PUT /api/v1/weddings/{id}/
    - PATCH /api/v1/weddings/{id}/
    """

    planner_name = serializers.CharField(source="planner.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Wedding
        fields = [
            "id",
            "groom_name",
            "bride_name",
            "date",
            "location",
            "budget",
            "status",
            "status_display",
            "planner_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "planner_name", "created_at", "updated_at"]

    def validate_budget(self, value):
        """Valida se o orçamento é positivo."""
        if value <= 0:
            raise serializers.ValidationError("O orçamento deve ser maior que zero.")
        return value

    def validate_date(self, value):
        """Valida se a data não é anterior ao dia atual."""
        from django.utils import timezone

        if value < timezone.localdate():
            raise serializers.ValidationError(
                "A data do casamento não pode ser anterior ao dia atual."
            )
        return value
