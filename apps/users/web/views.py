"""
Views customizadas do app users.

Nota: As views de signup e signin agora são gerenciadas pelo django-allauth
através de views customizadas em apps/users/allauth_views.py.
Mantemos aqui apenas as views específicas do nosso app.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from ..models import User
from .forms import CustomUserChangeForm


class EditProfileView(LoginRequiredMixin, UpdateView):
    """View para edição de perfil do usuário."""

    model = User
    form_class = CustomUserChangeForm
    template_name = "users/edit_profile.html"
    success_url = reverse_lazy("weddings:my_weddings")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request, "Seu perfil foi atualizado com sucesso!"
        )
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
