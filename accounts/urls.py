from django.urls import path

from . import views

app_name = "accounts"  # Adjust as per your app name

urlpatterns = [
    path("profile/", views.profile, name="profile"),
    path("edit-profile/", views.edit_profile, name="edit_profile"),
    path(
        "password-reset/", views.password_reset_request, name="password_reset_request"
    ),
    path("password-reset/sent/", views.password_reset_sent, name="password_reset_sent"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete/",
        views.password_reset_complete,
        name="password_reset_complete",
    ),
]
