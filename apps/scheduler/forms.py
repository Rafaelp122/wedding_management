from django import forms
from .models import Event
from apps.weddings.models import Wedding
from apps.core.utils.django_forms import add_placeholder
from apps.core.utils.mixins import FormStylingMixin
from django.utils import timezone


class EventForm(forms.ModelForm):
    """
    Formulário usado no modal de eventos do calendário.
    Possui campos visíveis para horários e um campo oculto para a data.
    """

    event_date = forms.DateField(widget=forms.HiddenInput(), required=True)

    # Campos de hora de início e fim (separados da data)
    start_time_input = forms.TimeField(
        label="Hora de Início",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        required=True,
    )

    end_time_input = forms.TimeField(
        label="Hora de Fim",
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
        required=False,
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "location",
            "description",
            "event_type",
            "event_date",
            "start_time_input",
            "end_time_input",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Reunião com Decorador"}
            ),
            "location": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Escritório Decoração Fina"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "event_type": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "title": "Título do Evento",
            "location": "Local",
            "description": "Descrição",
            "event_type": "Tipo de Evento",
        }

    def __init__(self, *args, **kwargs):
        # Permite pré-preencher os campos ao editar ou criar a partir de uma data clicada
        clicked_date = kwargs.pop("clicked_date", None)
        instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)

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

    def clean(self):
        """Combina data e hora nos campos 'start_time' e 'end_time'."""
        cleaned_data = super().clean()
        event_date = cleaned_data.get("event_date")
        start_time_input = cleaned_data.get("start_time_input")
        end_time_input = cleaned_data.get("end_time_input")

        if event_date and start_time_input:
            cleaned_data["start_time"] = f"{event_date} {start_time_input}"

        if event_date and end_time_input:
            cleaned_data["end_time"] = f"{event_date} {end_time_input}"

        return cleaned_data


class EventCrudForm(FormStylingMixin, forms.ModelForm):
    """Formulário completo para criar e editar eventos no painel administrativo."""

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Filtra os casamentos para exibir apenas os do planner logado
        if user:
            self.fields["wedding"].queryset = Wedding.objects.filter(planner=user)
        elif "wedding" in self.fields:
            self.fields["wedding"].queryset = Wedding.objects.none()

        # Adiciona placeholders para melhorar a experiência do usuário
        add_placeholder(self.fields["title"], "Ex: Reunião com fornecedor")
        add_placeholder(self.fields["description"], "Ex: Discutir flores e decoração")
        add_placeholder(self.fields["event_type"], "Selecione um tipo")
        add_placeholder(self.fields["wedding"], "Selecione um casamento (opcional)")

    class Meta:
        model = Event
        fields = [
            "title",
            "wedding",
            "start_time",
            "end_time",
            "event_type",
            "description",
            "location",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "title": "Título do Evento",
            "wedding": "Casamento Vinculado",
            "start_time": "Data e Hora de Início",
            "end_time": "Data e Hora de Fim",
            "event_type": "Tipo de Evento",
            "description": "Descrição",
            "location": "Local",
        }
