from django import forms
from apps.supplier.models import Supplier
from .models import Item


class ItemForm(forms.ModelForm):
    # Formulário baseado no modelo Item
    class Meta:
        model = Item
        fields = [
            "name",
            "quantity",
            "unit_price",
            "supplier",
            "category",
            "description",
        ]
        # Define os widgets para personalizar os campos no HTML
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ex: Buffet Completo"}
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "value": 1}),
            "unit_price": forms.NumberInput(
                attrs={"class": "form-control", "placeholder": "Ex: R$ 15.000,00"}
            ),
            "supplier": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        # Recebe o planner (usuário logado) para filtrar os fornecedores disponíveis
        planner = kwargs.pop("planner", None)
        super().__init__(*args, **kwargs)

        # Filtra os fornecedores vinculados ao planner atual
        if planner:
            self.fields["supplier"].queryset = Supplier.objects.filter(planner=planner)
