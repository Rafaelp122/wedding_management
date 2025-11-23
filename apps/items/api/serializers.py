"""
Serializers para a API REST de Item.
"""

from rest_framework import serializers

from apps.items.models import Item


class ItemListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listagem de itens.
    
    Usado no endpoint GET /api/v1/items/
    Retorna apenas informações essenciais para performance.
    """
    
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    wedding_couple = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "category",
            "category_display",
            "status",
            "status_display",
            "quantity",
            "unit_price",
            "total_cost",
            "supplier",
            "wedding",
            "wedding_couple",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "total_cost"]
    
    def get_wedding_couple(self, obj):
        """Retorna o nome do casal do casamento."""
        if obj.wedding:
            return str(obj.wedding)
        return None


class ItemDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalhes de um item específico.
    
    Usado no endpoint GET /api/v1/items/{id}/
    Inclui informações detalhadas e relacionamentos.
    """
    
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    wedding_couple = serializers.SerializerMethodField()
    wedding_date = serializers.DateField(
        source="wedding.date", read_only=True
    )
    
    # Contrato relacionado (se existir)
    contracts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_display",
            "status",
            "status_display",
            "quantity",
            "unit_price",
            "total_cost",
            "supplier",
            "wedding",
            "wedding_couple",
            "wedding_date",
            "contracts_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at", "total_cost"
        ]
    
    def get_wedding_couple(self, obj):
        """Retorna o nome do casal do casamento."""
        if obj.wedding:
            return str(obj.wedding)
        return None
    
    def get_contracts_count(self, obj):
        """Retorna o número de contratos associados ao item."""
        return 1 if hasattr(obj, 'contract') else 0


class ItemSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de itens.
    
    Usado nos endpoints:
    - POST /api/v1/items/
    - PUT /api/v1/items/{id}/
    - PATCH /api/v1/items/{id}/
    """
    
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    total_cost = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    
    class Meta:
        model = Item
        fields = [
            "id",
            "name",
            "description",
            "category",
            "category_display",
            "status",
            "status_display",
            "quantity",
            "unit_price",
            "total_cost",
            "supplier",
            "wedding",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at", "total_cost"
        ]
    
    def validate_unit_price(self, value):
        """Valida se o preço unitário não é negativo."""
        if value < 0:
            raise serializers.ValidationError(
                "O preço unitário não pode ser negativo."
            )
        return value
    
    def validate_quantity(self, value):
        """Valida se a quantidade é positiva."""
        if value <= 0:
            raise serializers.ValidationError(
                "A quantidade deve ser maior que zero."
            )
        return value
