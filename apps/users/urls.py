from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="users/login.html"),
        name="login",
    ),
    path(
        "deslogar/",
        auth_views.LogoutView.as_view(next_page="users:login"),
        name="logout",
    ),
    path("cadastro/", views.signup, name="signup"),
]
