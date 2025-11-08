from django.urls import path

from .views import (
                    AddItemView,
                    EditItemView,
                    PartialItemsView,
                    delete_item,
                    update_item_status,
)

app_name = "items"

urlpatterns = [
    path(
        '<int:wedding_id>/items/partial/',
        PartialItemsView.as_view(),
        name='partial_items'
    ),
    path(
        '<int:wedding_id>/items/add/',
        AddItemView.as_view(),
        name='add_item'
    ),
    path(
        'edit-item/<int:pk>/',
        EditItemView.as_view(),
        name='edit_item'
    ),
    path(
        'delete-item/<int:pk>/',
        delete_item,
        name='delete_item'
    ),
    path(
        'update-status/<int:pk>/',
        update_item_status,
        name='update_status'
    ),
]
