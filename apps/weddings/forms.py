from django import forms
from django.utils import timezone

from apps.core.utils.forms_utils import add_placeholder
from apps.core.mixins.forms import FormStylingMixin

from .models import Wedding


class WeddingForm(FormStylingMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["groom_name"], "Ex: Flavio")
        add_placeholder(self.fields["bride_name"], "Ex: Mirela")
        add_placeholder(self.fields["budget"], "Ex.: R$ 30.000,00")
        add_placeholder(
            self.fields["location"], "Ex.: Igreja Matriz, São Gonçalo, RJ"
        )

    class Meta:
        model = Wedding
        fields = ["groom_name", "bride_name", "date", "budget", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            "groom_name": "Noivo",
            "bride_name": "Noiva",
            "date": "Data",
            "budget": "Orçamento",
            "location": "Localização",
        }

    def clean_budget(self):
        """Valida se o orçamento é positivo."""
        budget = self.cleaned_data.get("budget")

        if budget is not None and budget <= 0:
            raise forms.ValidationError("O orçamento deve ser maior que zero.")

        return budget

    def clean_date(self):
        """Valida se a data não é anterior ao dia atual."""
        event_date = self.cleaned_data.get("date")

        if event_date and event_date < timezone.localdate():
            raise forms.ValidationError(
                "A data do casamento não pode ser anterior ao dia atual."
            )

        return event_date
