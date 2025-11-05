from django.urls import path
from . import views

app_name = "items"

urlpatterns = [
    path("partial/<int:wedding_id>/", views.partial_items, name="partial_items"),
    path("add/<int:wedding_id>/", views.add_item, name="add_item"),
    # Adicione uma URL para listar os itens, que será usada para cancelar
    # path('list/<int:wedding_id>/', views.list_items, name='list_items'),
]
