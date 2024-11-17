from django.urls import path
from . import views

app_name = "appointments"

urlpatterns = [
    path("time_slots/", views.time_slots, name="time_slots"),
    path("book/", views.book_appointment, name="book_appointment"),
    path("success/", views.appointment_success, name="appointment_success"),
    path("my-appointments/", views.my_appointments, name="my_appointments"),
    path(
        "cancel-appointment/<int:appointment_id>/",
        views.cancel_appointment,
        name="cancel_appointment",
    ),
    path(
        "reschedule_time_slots/",
        views.reschedule_time_slots,
        name="reschedule_time_slots",
    ),
    path(
        "update_appointment/",
        views.update_appointment,
        name="update_appointment",
    ),
]
