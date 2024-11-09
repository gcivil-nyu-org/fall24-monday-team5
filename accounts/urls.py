from django.urls import path

from . import views


app_name = 'accounts'  # Adjust as per your app name

urlpatterns = [
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
]