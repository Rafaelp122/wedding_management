from rest_framework import serializers
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    """Serializador que transforma o modelo Event em JSON compatível com FullCalendar."""

    start = serializers.DateTimeField(source="start_time")
    end = serializers.DateTimeField(source="end_time")

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "description",
            "event_type",
            "location",
            "wedding",
            "start",
            "end",
        ]
