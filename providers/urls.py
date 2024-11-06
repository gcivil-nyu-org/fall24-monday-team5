from django.urls import path
from . import views

app_name = "providers"

urlpatterns = [
    path("create-time-slot/", views.create_time_slot, name="create_time_slot"),
    path("", views.browse_providers, name="browse_providers"),
    path("<int:provider_id>/", views.provider_detail, name="provider_detail"),
]
