from django import forms

from apps.core.utils.django_forms import add_attr
from apps.core.utils.mixins import FormStylingMixin

from .models import Wedding


class WeddingForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                add_attr(field, 'class', 'form-check-input')
            else:
                add_attr(field, 'class', 'form-control ps-5')

            if field_name in self.errors:
                add_attr(field, 'class', 'is-invalid')

    class Meta:
        model = Wedding
        fields = ["groom_name", "bride_name", "date", "budget", "client", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
