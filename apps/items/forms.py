from django import forms

from apps.core.utils.forms_utils import add_placeholder
from apps.core.mixins.forms import FormStylingMixin

from .models import Item


class ItemForm(FormStylingMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona os placeholders dinamicamente
        add_placeholder(self.fields["name"], "Ex: Buffet Completo")
        add_placeholder(
            self.fields["description"], "Detalhes do item, observações, etc."
        )
        add_placeholder(self.fields["unit_price"], "Ex: 150.00")

    class Meta:
        model = Item

        fields = [
            "name",
            "category",
            # "status",
            "quantity",
            "unit_price",
            "description",
        ]

        labels = {
            "name": "Nome do Item",
            "category": "Categoria",
            # "status": "Status",
            "quantity": "Quantidade",
            "unit_price": "Preço Unitário",
            "description": "Descrição (Opcional)",
        }

        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "quantity": forms.NumberInput(attrs={"value": 1}),
        }

    def clean_quantity(self):
        """Valida se a quantidade é positiva."""
        quantity = self.cleaned_data.get("quantity")
        if quantity is not None and quantity <= 0:
            raise forms.ValidationError("A quantidade deve ser pelo menos 1.")
        return quantity

    def clean_unit_price(self):
        """Valida se o preço não é negativo."""
        unit_price = self.cleaned_data.get("unit_price")
        if unit_price is not None and unit_price < 0:
            raise forms.ValidationError("O preço unitário não pode ser negativo.")
        return unit_price
