import logging
from typing import ClassVar

from django import forms
from django.utils import timezone

from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder

from ..models import Event

logger = logging.getLogger(__name__)


class EventForm(FormStylingMixin, forms.ModelForm):
    """
    Formulário para criação e edição de eventos no calendário.
    Herda de FormStylingMixin para aplicar classes Bootstrap automaticamente.
    """

    start_time_input = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=True,
        label="Horário de início",
    )

    end_time_input = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=False,
        label="Horário de fim",
    )

    class Meta:
        model = Event
        fields: ClassVar[list] = [
            "title",
            "event_type",
            "location",
            "description",
        ]
        labels: ClassVar[dict] = {
            "title": "Título do Evento",
            "location": "Local",
            "description": "Descrição",
            "event_type": "Tipo de Evento",
        }
        widgets: ClassVar[dict] = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    field_order: ClassVar[list] = [
        "title",
        "event_type",
        "start_time_input",
        "end_time_input",
        "location",
        "description",
    ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["title"], "Ex: Reunião com Decorador")
        add_placeholder(self.fields["location"], "Ex: Escritório Decoração Fina")
        add_placeholder(
            self.fields["description"],
            "Ex: Pauta da reunião: definir cardápio, decoração e lista de músicas",
        )

        # Preenche os campos ao editar um evento existente
        if instance:
            if instance.start_time:
                local_start_time = timezone.localtime(instance.start_time)
                self.fields["start_time_input"].initial = local_start_time.time()

            if instance.end_time:
                local_end_time = timezone.localtime(instance.end_time)
                self.fields["end_time_input"].initial = local_end_time.time()

    def clean_end_time_input(self):
        """Valida se o horário de fim é posterior ao horário de início."""
        end_time = self.cleaned_data.get("end_time_input")
        start_time = self.cleaned_data.get("start_time_input")

        if end_time and start_time and end_time <= start_time:
            logger.warning(
                "Tentativa de cadastro com horário de fim antes do início: %s <= %s",
                end_time,
                start_time,
            )
            raise forms.ValidationError(
                "O horário de fim deve ser posterior ao horário de início."
            )

        return end_time

    def get_start_time_input(self):
        """Retorna o horário de início do formulário."""
        return self.cleaned_data.get("start_time_input")

    def get_end_time_input(self):
        """Retorna o horário de fim do formulário."""
        return self.cleaned_data.get("end_time_input")
