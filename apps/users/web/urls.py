from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    # Edição de perfil (mantida customizada)
    path(
        "editar-perfil/",
        views.EditProfileView.as_view(),
        name="edit_profile",
    ),
    # As rotas de signup, login e logout agora são gerenciadas pelo allauth em /accounts/
]
