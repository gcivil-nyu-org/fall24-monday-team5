from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required


def error(request):
    return render(request, "error.html")


def home(request):
    if request.user.is_authenticated:
        if request.user.role == "User":
            return redirect("accounts:client_dashboard")
        elif request.user.role == "Provider":
            return redirect("accounts:provider_dashboard")
        # You can add additional roles if needed or default to a specific dashboard
    return redirect("login")

@login_required
def log_out(request):
    logout(request)
    return redirect("login")


def log_in(request):
    login(request)
    return redirect("time_slots")