import logging
from datetime import datetime

from django import forms
from django.utils import timezone

from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder

from .models import Event

logger = logging.getLogger(__name__)


class EventForm(FormStylingMixin, forms.ModelForm):
    """
    Formulário para criação e edição de eventos no calendário.
    Herda de FormStylingMixin para aplicar classes Bootstrap automaticamente.
    """

    event_date = forms.DateField(widget=forms.HiddenInput(), required=True)

    start_time_input = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=True,
    )

    end_time_input = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time"}),
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "location",
            "description",
            "event_type",
        ]
        labels = {
            "title": "Título do Evento",
            "location": "Local",
            "description": "Descrição",
            "event_type": "Tipo de Evento",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        clicked_date = kwargs.pop("clicked_date", None)
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["title"], "Ex: Reunião com Decorador")
        add_placeholder(self.fields["location"], "Ex: Escritório Decoração Fina")

        # Preenche os campos ao editar um evento existente
        if instance:
            if instance.start_time:
                local_start_time = timezone.localtime(instance.start_time)
                self.fields["event_date"].initial = local_start_time.date()
                self.fields["start_time_input"].initial = local_start_time.time()

            if instance.end_time:
                local_end_time = timezone.localtime(instance.end_time)
                self.fields["end_time_input"].initial = local_end_time.time()

        # Preenche a data com o dia clicado no calendário
        elif clicked_date:
            self.fields["event_date"].initial = clicked_date

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

    def save(self, commit=True):
        """
        Combina data e hora nos campos start_time e end_time.

        Args:
            commit: Se True, salva no banco. Se False, apenas prepara a instância.

        Returns:
            Instância do Event com datas combinadas.
        """
        instance = super().save(commit=False)

        event_date = self.cleaned_data.get("event_date")
        start_time_input = self.cleaned_data.get("start_time_input")
        end_time_input = self.cleaned_data.get("end_time_input")

        # Combina data + hora de início
        if event_date and start_time_input:
            instance.start_time = timezone.make_aware(
                datetime.combine(event_date, start_time_input)
            )

        # Combina data + hora de fim (opcional)
        if event_date and end_time_input:
            instance.end_time = timezone.make_aware(
                datetime.combine(event_date, end_time_input)
            )

        if commit:
            instance.save()

        return instance
