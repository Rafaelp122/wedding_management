# weddings/urls.py

from django.urls import path
from . import views

app_name = "weddings"

urlpatterns = [
    # A view de criação continua sendo uma função, então não muda
    path("create/", views.create_wedding_flow, name="create_wedding_flow"),

    # As URLs abaixo AGORA apontam para as Class-Based Views
    path("my-weddings/", views.WeddingListView.as_view(), name="my_weddings"),
    path("detail/<int:wedding_id>/", views.WeddingDetailView.as_view(), name="wedding_detail"),
    path("edit/<int:id>/", views.WeddingUpdateView.as_view(), name="edit_wedding"),
    
    # A view de deleção agora usa a CBV e espera um POST, mas a URL pode ser a mesma
    path("delete/<int:id>/", views.WeddingDeleteView.as_view(), name="delete_wedding"),
]