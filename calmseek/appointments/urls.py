from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('time_slots/', views.time_slots, name='time_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('success/', views.appointment_success, name='appointment_success'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    # Cancel appointment

]
