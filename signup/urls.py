from django.urls import path
from . import views

app_name = "signup"

urlpatterns = [
    path("select_role/", views.select_role, name="select_role"),
    path("signup_provider/", views.signup_provider, name="signup_provider"),
    path("signup_user/", views.signup_user, name="signup_user"),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/sent/', views.password_reset_sent, name='password_reset_sent'),
    path('password-reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset-complete/', views.password_reset_complete, name='password_reset_complete'),
]
