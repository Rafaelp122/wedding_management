# users/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from apps.users.models import Planner


class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=255, label="Nome completo")
    cpf_cnpj = forms.CharField(max_length=20, label="CPF ou CNPJ")
    email = forms.EmailField(label="Email")
    phone = forms.CharField(max_length=20, label="Telefone")

    class Meta:
        model = User
        fields = ["username", "password1", "password2", "email"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Cria o Planner
            Planner.objects.create(
                user=user,
                name=self.cleaned_data["name"],
                cpf_cnpj=self.cleaned_data["cpf_cnpj"],
                email=self.cleaned_data["email"],
                phone=self.cleaned_data["phone"],
            )
        return user
