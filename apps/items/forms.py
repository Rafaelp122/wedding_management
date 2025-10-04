from django import forms

from apps.supplier.models import Supplier

from .models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'quantity', 'unit_price', 'supplier', 'category','description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Buffet Completo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'value': 1}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: R$ 15.000,00'}),
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        planner = kwargs.pop('planner', None)
        super().__init__(*args, **kwargs)
        if planner:
            self.fields['supplier'].queryset = Supplier.objects.filter(planner=planner)
