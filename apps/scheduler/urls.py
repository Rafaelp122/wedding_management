from django.urls import path
from . import views

app_name = "scheduler"


urlpatterns = [
    path("partial/<int:wedding_id>/", views.partial_scheduler, name="partial_scheduler"),
]
