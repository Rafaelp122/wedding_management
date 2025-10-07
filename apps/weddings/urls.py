# weddings/urls.py

from django.urls import path

from . import views

app_name = "weddings"

urlpatterns = [
    path("my-weddings/", views.WeddingListView.as_view(), name="my_weddings"),
    path("detail/<int:wedding_id>/", views.WeddingDetailView.as_view(), name="wedding_detail"),
    path("edit/<int:id>/", views.WeddingUpdateView.as_view(), name="edit_wedding"),
    path("delete/<int:id>/", views.WeddingDeleteView.as_view(), name="delete_wedding"),
]