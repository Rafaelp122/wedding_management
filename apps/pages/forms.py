import logging

from django import forms

from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder

from .models import ContactInquiry

logger = logging.getLogger(__name__)


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

    def clean(self):
        """
        Loga erros de validação para monitoramento.
        """
        cleaned_data = super().clean()
        if self.errors:
            logger.warning(f"Erro no formulário de contato: {self.errors}")
        return cleaned_data
