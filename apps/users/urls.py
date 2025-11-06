from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("cadastrar/", views.SignUpView.as_view(), name="sign_up"),
    path("login/", views.SignInView.as_view(), name="sign_in"),
    path(
        "deslogar/",
        auth_views.LogoutView.as_view(next_page="users:sign_in"),
        name="logout",
    ),
]
