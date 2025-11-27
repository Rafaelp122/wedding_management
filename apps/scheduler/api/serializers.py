"""
Serializers da API de Events (Scheduler).
"""
from rest_framework import serializers

from apps.scheduler.models import Event


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer para criação e atualização de eventos.

    Usado nos endpoints:
    - POST /api/v1/scheduler/events/
    - PUT/PATCH /api/v1/scheduler/events/{id}/
    """

    class Meta:
        model = Event
        fields = [
            "id",
            "wedding",
            "planner",
            "title",
            "location",
            "description",
            "event_type",
            "start_time",
            "end_time",
        ]
        read_only_fields = ["id"]

    def validate(self, data):
        """Valida que o horário de início é anterior ao de término."""
        start = data.get("start_time")
        end = data.get("end_time")

        if start and end and start >= end:
            raise serializers.ValidationError({
                "end_time": "O horário de término deve ser posterior ao de início."
            })

        return data


class EventListSerializer(serializers.ModelSerializer):
    """
    Serializer otimizado para listagem de eventos.

    Usado em:
    - GET /api/v1/scheduler/events/

    Inclui campos calculados:
    - wedding_couple: Nome do casal do casamento
    - duration_minutes: Duração do evento em minutos
    """
    wedding_couple = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "wedding",
            "wedding_couple",
            "planner",
            "title",
            "location",
            "event_type",
            "start_time",
            "end_time",
            "duration_minutes",
        ]

    def get_wedding_couple(self, obj):
        """Retorna o nome do casal do casamento."""
        if obj.wedding:
            return str(obj.wedding)
        return None

    def get_duration_minutes(self, obj):
        """Retorna a duração do evento em minutos."""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        return None


class EventDetailSerializer(serializers.ModelSerializer):
    """
    Serializer com detalhes completos do evento.

    Usado em:
    - GET /api/v1/scheduler/events/{id}/

    Inclui informações completas + campos calculados:
    - wedding_couple: Nome do casal
    - wedding_date: Data do casamento
    - duration_minutes: Duração em minutos
    - is_past: Se o evento já passou
    """
    wedding_couple = serializers.SerializerMethodField()
    wedding_date = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    is_past = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            "id",
            "wedding",
            "wedding_couple",
            "wedding_date",
            "planner",
            "title",
            "location",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "duration_minutes",
            "is_past",
        ]
        read_only_fields = ["id", "is_past"]

    def get_wedding_couple(self, obj):
        """Retorna o nome do casal do casamento."""
        if obj.wedding:
            return str(obj.wedding)
        return None

    def get_wedding_date(self, obj):
        """Retorna a data do casamento."""
        if obj.wedding:
            return obj.wedding.date
        return None

    def get_duration_minutes(self, obj):
        """Retorna a duração do evento em minutos."""
        if obj.start_time and obj.end_time:
            delta = obj.end_time - obj.start_time
            return int(delta.total_seconds() / 60)
        return None

    def get_is_past(self, obj):
        """Retorna True se o evento já passou."""
        from django.utils import timezone
        if obj.end_time:
            return obj.end_time < timezone.now()
        if obj.start_time:
            return obj.start_time < timezone.now()
        return False
