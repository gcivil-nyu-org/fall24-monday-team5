from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('time_slots/', views.time_slots, name='time_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('success/', views.appointment_success, name='appointment_success'),
    path('provider/create-time-slot/', views.create_time_slot, name='create_time_slot'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('reschedule_time_slots/<int:appointment_id>/', views.reschedule_time_slots, name='reschedule_time_slots'),
    path('update_appointment/<int:appointment_id>/<int:slot_id>/', views.update_appointment, name='update_appointment'),
]
