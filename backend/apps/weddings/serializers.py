# apps/weddings/serializers.py
from apps.core.serializers import BaseSerializer

from .models import Wedding


class WeddingSerializer(BaseSerializer):
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
        ]
