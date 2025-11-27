# weddings/urls.py

from django.urls import path

from .views import (
    UpdateWeddingStatusView,
    WeddingCreateView,
    WeddingDeleteView,
    WeddingDetailView,
    WeddingListView,
    WeddingUpdateView,
)

app_name = "weddings"

urlpatterns = [
    path("my-weddings/", WeddingListView.as_view(), name="my_weddings"),
    path(
        "detail/<int:wedding_id>/",
        WeddingDetailView.as_view(),
        name="wedding_detail",
    ),
    path("edit/<int:id>/", WeddingUpdateView.as_view(), name="edit_wedding"),
    path("delete/<int:id>/", WeddingDeleteView.as_view(), name="delete_wedding"),
    path("create/", WeddingCreateView.as_view(), name="create_wedding"),
    path(
        "update-status/<int:id>/",
        UpdateWeddingStatusView.as_view(),
        name="update_wedding_status",
    ),
]
