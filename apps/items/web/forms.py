import logging
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona os placeholders dinamicamente
        add_placeholder(self.fields["name"], "Ex: Buffet Completo")
        add_placeholder(
            self.fields["description"], "Detalhes do item, observações, etc."
        )
        add_placeholder(self.fields["unit_price"], "Ex: 150.00")
        add_placeholder(self.fields["supplier"], "Ex: Floricultura")

        # Forçamos o min="1" aqui, pois o PositiveIntegerField do model forçava "0"
        self.fields["quantity"].widget.attrs["min"] = 1
        self.fields["quantity"].widget.attrs["value"] = 1  # Valor inicial visual

        # Garantimos o preço também
        self.fields["unit_price"].widget.attrs["min"] = 0
        self.fields["unit_price"].widget.attrs["step"] = "0.01"

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
            "unit_price": "Preço Unitário",
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
            # Loga o erro antes de lançar a exceção
            logger.warning(
                f"Tentativa de cadastro de item com quantidade inválida: {quantity}"
            )
            raise forms.ValidationError("A quantidade deve ser pelo menos 1.")
        return quantity

    def clean_unit_price(self):
        """Valida se o preço não é negativo."""
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price is not None and unit_price < 0:
            logger.warning(
                f"Tentativa de cadastro de item com preço negativo: {unit_price}"
            )
            raise forms.ValidationError("O preço unitário não pode ser negativo.")
        return unit_price
