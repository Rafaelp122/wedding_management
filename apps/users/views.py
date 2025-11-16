from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from apps.core.mixins.auth import RedirectAuthenticatedUserMixin

from .forms import CustomUserChangeForm, CustomUserCreationForm, SignInForm
from .models import User


class SignUpView(RedirectAuthenticatedUserMixin, CreateView):
    template_name = "users/sign_up.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("users:sign_in")

    def form_valid(self, form):
        messages.success(
            self.request, "Cadastro realizado com sucesso! Faça login para continuar."
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout_dict"] = {
            "username": "col-md-6",
            "first_name": "col-md-6",
            "last_name": "col-md-6",
            "email": "col-md-6",
            "password1": "col-md-6",
            "password2": "col-md-6",
        }

        context["form_icons"] = {
            "username": "fas fa-user",
            "email": "fas fa-envelope",
            "first_name": "fas fa-id-card",
            "last_name": "fas fa-id-card",
            "password1": "fas fa-lock",
            "password2": "fas fa-lock",
        }

        context["form_action"] = reverse_lazy("users:sign_up")
        context["button_text"] = "Enviar"
        context["default_column_class"] = "col-md-6"

        return context


class SignInView(RedirectAuthenticatedUserMixin, LoginView):
    template_name = "users/sign_in.html"
    form_class = SignInForm

    def form_valid(self, form):
        messages.success(self.request, "Login bem sucedido!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Usuário ou senha inválidos")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout_dict"] = {
            "username": "col-md-12",
            "password": "col-md-12",
        }

        context["form_icons"] = {
            "username": "fas fa-user",
            "password": "fas fa-lock",
        }

        context["form_action"] = reverse_lazy("users:sign_in")
        context["button_text"] = "Entrar"
        context["default_column_class"] = "col-md-6"
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("weddings:my_weddings")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Seu perfil foi atualizado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_layout_dict"] = {
            "username": "col-md-12",
            "email": "col-md-12",
            "first_name": "col-md-6",
            "last_name": "col-md-6",
        }

        context["form_action"] = reverse_lazy("users:edit_profile")
        context["button_text"] = "Salvar Alterações"
        context["form_icons"] = {
            "username": "fas fa-user",
            "email": "fas fa-envelope",
            "first_name": "fas fa-id-card",
            "last_name": "fas fa-id-card",
        }
        return context
