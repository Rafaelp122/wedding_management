from django import forms
from .models import ContactInquiry
from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder


class ContactForm(FormStylingMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_placeholder(self.fields["name"], "Ex: Maria Silva")
        add_placeholder(self.fields["email"], "Ex: maria.silva@email.com")
        add_placeholder(self.fields["message"], "Digite sua mensagem aqui...")

    class Meta:
        model = ContactInquiry
        fields = ["name", "email", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "name": "Nome",
            "email": "E-mail",
            "message": "Mensagem",
        }
