from django import forms

from .models import Wedding


class WeddingForm(forms.ModelForm):
    class Meta:
        model = Wedding
        fields = ["groom_name", "bride_name", "date", "location"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
