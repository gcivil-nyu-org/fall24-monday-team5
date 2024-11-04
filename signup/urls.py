from django.urls import path
from . import views

app_name = "signup"

urlpatterns = [
    path("select_role/", views.select_role, name="select_role"),
    path("signup_provider/", views.signup_provider, name="signup_provider"),
    path("signup_user/", views.signup_user, name="signup_user"),
]
