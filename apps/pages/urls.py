from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("fale-conosco/", views.ContactUsView.as_view(), name="contact_us"),
]
