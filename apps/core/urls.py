from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("contact-us/", views.contact_us, name="contact-us"),
]
