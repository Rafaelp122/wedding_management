from rest_framework import serializers

from apps.core.serializers import BaseSerializer
from apps.weddings.models import Wedding

from .models import Event


class EventSerializer(BaseSerializer):
    """
    Serializer para o modelo de Eventos (Calendário).
    Responsável pela validação inicial e representação JSON dos dados.
    """

    # Representamos o casamento pelo UUID para facilitar o consumo pela API/Frontend
    wedding = serializers.SlugRelatedField(
        slug_field="uuid",
        queryset=Wedding.objects.all(),
        help_text="UUID do Casamento vinculado",
    )

    class Meta(BaseSerializer.Meta):
        model = Event
        fields = [
            *BaseSerializer.Meta.fields,
            "wedding",
            "title",
            "location",
            "description",
            "event_type",
            "start_time",
            "end_time",
            "reminder_enabled",
            "reminder_minutes_before",
        ]

    def validate(self, data):
        """
        Executa validações cruzadas de campos (RF12).
        """
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        # Regra de Negócio: Fim do evento deve ser posterior ao início
        if start_time and end_time and end_time < start_time:
            raise serializers.ValidationError(
                {
                    "end_time": "A hora de término não pode ser anterior à hora de "
                    "início."
                }
            )

        # Regra de Negócio: Lembretes só fazem sentido se forem minutos positivos
        reminder_minutes = data.get("reminder_minutes_before")
        if reminder_minutes is not None and reminder_minutes < 0:
            raise serializers.ValidationError(
                {
                    "reminder_minutes_before": "Os minutos do lembrete devem ser "
                    "um valor positivo."
                }
            )

        return data
