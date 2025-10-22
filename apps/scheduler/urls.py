# Em scheduler/urls.py

from django.urls import path
from . import views

# app_name é VITAL para a tag {% url %} funcionar
app_name = 'scheduler' 

urlpatterns = [
    # URL que o HTMX está chamando:
    path(
        'partial/<int:wedding_id>/', 
        views.partial_scheduler, 
        name='partial_scheduler'
    ),
    
    # Futuramente, você adicionará URLs para criar/editar/excluir eventos:
    # path('create-event/<int:wedding_id>/', views.create_event_view, name='create_event'),
    # path('update-event/<int:event_id>/', views.update_event_view, name='update_event'),
]