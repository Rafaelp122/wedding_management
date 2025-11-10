from django.urls import path
from . import views

# Define o namespace para o app de pages
app_name = "pages"

# Rotas das páginas estáticas do site
urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),  # Página inicial
    path("fale-conosco/", views.ContactUsView.as_view(), name="contact_us"),  # Página de contato
]
