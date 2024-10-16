from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('time_slots/', views.time_slots, name='time_slots'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
    path('success/', views.appointment_success, name='appointment_success'),
    path('provider/create-time-slot/', views.create_time_slot, name='create_time_slot'),
    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
]
