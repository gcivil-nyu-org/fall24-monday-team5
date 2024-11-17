from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required


def error(request):
    return render(request, "error.html")

@login_required
def log_out(request):
    logout(request)
    return redirect("login")

def log_in(request):
    login(request)
    return redirect("time_slots")