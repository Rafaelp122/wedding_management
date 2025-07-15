from django.urls import path

from . import views

app_name = "weddings"

urlpatterns = [
    path("", views.my_weddings, name="my_weddings"),
    path("novo-casamento/", views.create_wedding, name="create_wedding"),
    path('<int:id>/editar-casamento/', views.edit_wedding, name='edit_wedding'),
    path('<int:id>/excluir-casamento/', views.delete_wedding, name='delete_wedding'),
]
