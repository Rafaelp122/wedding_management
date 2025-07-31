from django.urls import path
from . import views


app_name = "items"

urlpatterns = [
    path("partial/<int:wedding_id>/", views.partial_items, name="partial_items"),
]
