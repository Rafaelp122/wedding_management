from django import forms

from apps.core.utils.django_forms import add_placeholder
from apps.core.utils.mixins import FormStylingMixin

from .models import Wedding


class WeddingForm(FormStylingMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields['groom_name'], 'Ex: Flavio')
        add_placeholder(self.fields['bride_name'], 'Ex: Mirela')
        add_placeholder(self.fields['budget'], 'Ex.: R$ 30.000,00')
        add_placeholder(self.fields['location'], 'Ex.: Igreja Matriz, São Gonçalo, RJ')

    class Meta:
        model = Wedding
        fields = ["groom_name", "bride_name", "date", "budget", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
        labels = {
            'date': 'Data',
        }

    groom_name = forms.CharField(
        label="Noivo",
    )

    bride_name = forms.CharField(
        label="Noiva",
    )

    budget = forms.DecimalField(
        label="Orçamento",
    )

    location = forms.CharField(
        label="Localização",
    )
