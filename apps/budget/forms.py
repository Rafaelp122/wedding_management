from django import forms
from .models import Budget


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ["initial_estimate"]
        widgets = {
            "initial_estimate": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex: 50000.00",
                    "step": "1000",
                    "min": "0",
                }
            )
        }
        labels = {"initial_estimate": "Estimativa de Orçamento Inicial"}
