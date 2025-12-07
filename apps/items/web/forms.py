import logging
from decimal import Decimal, InvalidOperation
from typing import Any, ClassVar

from django import forms

from apps.core.mixins.forms import FormStylingMixin
from apps.core.utils.forms_utils import add_placeholder

from ..models import Item

logger = logging.getLogger(__name__)


class ItemForm(FormStylingMixin, forms.ModelForm):
    """
    Formulário para criação e edição de Itens do Orçamento.
    """

    # 1. Redefinimos como CharField para aceitar a máscara (R$, vírgula, etc)
    unit_price = forms.CharField(
        label="Preço Unitário",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "currency-input",  # A classe mágica para o seu JS
                "inputmode": "numeric",  # Teclado numérico no mobile
                "placeholder": "R$ 0,00",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona os placeholders
        add_placeholder(self.fields["name"], "Ex: Buffet Completo")
        add_placeholder(
            self.fields["description"], "Detalhes do item, observações, etc."
        )
        # O placeholder do unit_price já foi definido no widget acima
        add_placeholder(self.fields["supplier"], "Ex: Floricultura")

        # Configuração da Quantidade (Mantida)
        self.fields["quantity"].widget.attrs["min"] = 1
        # Se for criação (sem instancia), sugere 1 visualmente
        if not self.instance.pk:
            self.fields["quantity"].widget.attrs["value"] = 1

        # 2. Se for edição, formata o preço do banco (150.00) para visual (R$ 150,00)
        if self.instance and self.instance.pk and self.instance.unit_price:
            formatted_value = f"{self.instance.unit_price:,.2f}"
            # Troca padrão US para BR
            formatted_value = (
                formatted_value.replace(",", "X").replace(".", ",").replace("X", ".")
            )
            self.fields["unit_price"].initial = f"R$ {formatted_value}"

    class Meta:
        model = Item

        fields: ClassVar[list[str]] = [
            "name",
            "category",
            "quantity",
            "unit_price",
            "supplier",
            "description",
        ]

        labels: ClassVar[dict[str, str]] = {
            "name": "Nome do Item",
            "category": "Categoria",
            "quantity": "Quantidade",
            # "unit_price": Definido manualmente acima
            "supplier": "Fornecedor",
            "description": "Descrição (Opcional)",
        }

        widgets: ClassVar[dict[str, Any]] = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_quantity(self):
        """Valida se a quantidade é positiva."""
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            logger.warning(
                f"Tentativa de cadastro de item com quantidade inválida: {quantity}"
            )
            raise forms.ValidationError("A quantidade deve ser pelo menos 1.")
        return quantity

    def clean_unit_price(self):
        """
        Recebe: 'R$ 150,00' (String visual)
        Transforma em: 150.00 (Decimal puro para o banco)
        """
        price_str = self.cleaned_data.get("unit_price")

        if not price_str:
            return None

        # Limpeza robusta
        clean_value = (
            price_str.replace("R$", "")
            .replace("\xa0", "")  # Remove espaço non-breaking
            .replace(" ", "")
            .replace(".", "")  # Remove ponto de milhar
            .replace(",", ".")  # Troca vírgula por ponto
        )

        try:
            price_decimal = Decimal(clean_value)
        except (ValueError, InvalidOperation):
            logger.warning("Erro de conversão no preço do item. Input: '%s'", price_str)
            raise forms.ValidationError(
                "Valor inválido. Digite apenas números."
            ) from None

        if price_decimal < 0:
            logger.warning(
                f"Tentativa de cadastro de item com preço negativo: {price_decimal}"
            )
            raise forms.ValidationError("O preço unitário não pode ser negativo.")

        return price_decimal
