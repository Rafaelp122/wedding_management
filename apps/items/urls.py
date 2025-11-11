from django.urls import path

from .views import (
                    AddItemView,
                    EditItemView,
                    ItemDeleteView,
                    ItemListView,
                    UpdateItemStatusView,
)

# Define o namespace para o app de itens
app_name = "items"

# Rotas do app de itens (itens do orçamento vinculados ao casamento)
urlpatterns = [
    # Exibe a lista parcial de itens de um casamento específico
    path(
        "<int:wedding_id>/items/partial/",
        ItemListView.as_view(),
        name="partial_items"
    ),
    # Adiciona um novo item ao casamento
    path(
        "<int:wedding_id>/items/add/",
        AddItemView.as_view(),
        name="add_item"
    ),
    # Edita um item existente
    path(
        "edit-item/<int:pk>/",
        EditItemView.as_view(),
        name="edit_item"
    ),
    # Exclui um item
    path(
        "delete-item/<int:pk>/",
        ItemDeleteView.as_view(),
        name="delete_item"
    ),
    # Atualiza o status de um item (pendente, em andamento, concluído)
    path(
        "update-status/<int:pk>/",
        UpdateItemStatusView.as_view(),
        name="update_status"
    ),
]
