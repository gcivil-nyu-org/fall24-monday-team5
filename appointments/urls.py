from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("time_slots/", views.time_slots, name="time_slots"),
    path("book/<int:slot_id>/", views.book_appointment, name="book_appointment"),
    path("success/", views.appointment_success, name="appointment_success"),
    path("provider/create-time-slot/", views.create_time_slot, name="create_time_slot"),
    path("dashboard/", views.dashboard, name="provider_dashboard"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path("favorites/", views.favorite_providers, name="favorite_providers"),
    path(
        "cancel-appointment/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path(
        "reschedule_time_slots/<int:appointment_id>/",
        views.reschedule_time_slots,
        name="reschedule_time_slots",
    ),
    path(
        "update_appointment/<int:appointment_id>/<int:slot_id>/",
        views.update_appointment,
        name="update_appointment",
    ),
    path("delete-slot/<int:slot_id>/", views.delete_slot, name="delete_slot"),
    path("providers/", views.browse_providers, name="browse_providers"),
    path("providers/<int:provider_id>/", views.provider_detail, name="provider_detail"),
    path(
        "providers/<int:provider_id>/add_to_favorites/",
        views.add_to_favorites,
        name="add_to_favorites",
    ),
    path(
        "providers/<int:provider_id>/remove_from_favorites/",
        views.remove_from_favorites,
        name="remove_from_favorites",
    ),
    path(
        "providers/<int:provider_id>/delete/",
        views.delete_favorite_provider,
        name="delete_favorite_provider",
    ),
]
