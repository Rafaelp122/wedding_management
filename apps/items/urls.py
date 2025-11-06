from django.urls import path

from .views import AddItemView, PartialItemsView

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
        name='add_item'),
]
