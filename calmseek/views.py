from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.messages import get_messages
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

def login_user(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # should be change into a main page later
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


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
    # Clear Messages on Logout
    storage = get_messages(request)
    list(storage)
    logout(request)
    return redirect("login")
