# apps/weddings/serializers.py
from rest_framework import serializers

from apps.core.serializers import BaseSerializer

from .models import Wedding


class WeddingSerializer(BaseSerializer):
    total_budget = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        write_only=True,
        required=True,
        help_text="Valor total do orçamento inicial que será criado para "
        "este casamento.",
    )

    class Meta(BaseSerializer.Meta):
        model = Wedding
        fields = [
            *BaseSerializer.Meta.fields,
            "groom_name",
            "bride_name",
            "date",
            "location",
            "expected_guests",
            "status",
            "total_budget",
        ]
