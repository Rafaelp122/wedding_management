from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    path('partial/<int:wedding_id>/', views.partial_budget, name='partial_budget'),
]
