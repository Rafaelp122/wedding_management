import logging
from decimal import Decimal, InvalidOperation
from typing import ClassVar

from django import forms
from django.utils import timezone

from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder
from apps.weddings.models import Wedding

logger = logging.getLogger(__name__)


class WeddingForm(FormStylingMixin, forms.ModelForm):
    """
    Formulário para criação e edição de casamentos.
    Herda de FormStylingMixin para aplicar classes Bootstrap automaticamente.
    """

    # 1. Definimos como CharField para aceitar "R$ ..." sem erro de validação inicial
    budget = forms.CharField(
        label="Orçamento",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "currency-input",  # Classe para o JavaScript pegar
                "inputmode": "numeric",  # Abre teclado numérico no celular
                "placeholder": "R$ 0,00",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        add_placeholder(self.fields["groom_name"], "Ex: Flavio")
        add_placeholder(self.fields["bride_name"], "Ex: Mirela")
        add_placeholder(self.fields["location"], "Ex.: Igreja Matriz, São Gonçalo, RJ")

        # 2. Se for edição, converte o Decimal do banco (30000.00) para Texto (R$ 30.000,00)
        if self.instance and self.instance.pk and self.instance.budget:
            formatted_value = f"{self.instance.budget:,.2f}"
            # Troca padrão US para BR
            formatted_value = (
                formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.fields["budget"].initial = f"R$ {formatted_value}"

    class Meta:
        model = Wedding
        fields: ClassVar[list[str]] = [
            "groom_name",
            "bride_name",
            "date",
            "budget",
            "location",
        ]
        labels: ClassVar[dict] = {
            "groom_name": "Noivo",
            "bride_name": "Noiva",
            "date": "Data",
            # "budget" já está definido manualmente lá em cima
            "location": "Localização",
        }
        widgets: ClassVar[dict] = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "location": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_budget(self):
        """
        Recebe: 'R$ 1.500,50' (String visual)
        Transforma em: 1500.50 (Decimal puro para o banco)
        """
        budget_str = self.cleaned_data.get("budget")

        if not budget_str:
            return None

        # Limpeza robusta: tira R$, espaços, pontos de milhar e troca vírgula por ponto
        clean_value = (
            budget_str.replace("R$", "")
            .replace("\xa0", "")  # Remove espaço non-breaking se houver
            .replace(" ", "")
            .replace(".", "")  # Remove separador de milhar
            .replace(",", ".")  # Transforma vírgula decimal em ponto
        )

        try:
            budget_decimal = Decimal(clean_value)
        except (ValueError, InvalidOperation):
            # Loga o erro com o valor original e o valor limpo para debug
            logger.warning(
                "Erro de conversão no orçamento. Input original:"
                " '%s' | Tentativa limpa: '%s'",
                budget_str,
                clean_value,
            )
            # 'from None' satisfaz o Ruff e limpa o traceback
            raise forms.ValidationError(
                "Valor inválido. Digite apenas números."
            ) from None

        if budget_decimal <= 0:
            logger.warning(
                "Tentativa de cadastro com orçamento inválido: %s", budget_decimal
            )
            raise forms.ValidationError("O orçamento deve ser maior que zero.")

        return budget_decimal

    def clean_date(self):
        """Valida se a data não é anterior ao dia atual."""
        event_date = self.cleaned_data.get("date")

        if event_date and event_date < timezone.localdate():
            logger.warning("Tentativa de cadastro com data passada: %s", event_date)
            raise forms.ValidationError(
                "A data do casamento não pode ser anterior ao dia atual."
            )

        return event_date
