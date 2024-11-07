from django.urls import path

from client import views

app_name = "client"

urlpatterns = [
    path("favorites/", views.favorite_providers, name="favorite_providers"),
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
