from django.urls import path
from . import views

app_name = "scheduler"

urlpatterns = [
    path("list/", views.EventListView.as_view(), name="list"),
    path("new/", views.EventCreateView.as_view(), name="new"),
    path("edit/<int:event_id>/", views.EventUpdateView.as_view(), name="edit"),
    path("delete/<int:event_id>/", views.EventDeleteView.as_view(), name="delete"),
    path(
        "partial/<int:wedding_id>/",
        views.PartialSchedulerView.as_view(),
        name="partial_scheduler",
    ),
    path("api/events/<int:wedding_id>/", views.event_api, name="event_api"),
    path(
        "manage/<int:wedding_id>/", views.ManageEventView.as_view(), name="manage_event"
    ),
]
