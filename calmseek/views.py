from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required


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
                return redirect("appointments:time_slots")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})


def error(request):
    return render(request, "error.html")


@login_required
def log_out(request):
    logout(request)
    return redirect("login")


def log_in(request):
    login(request)
    return redirect("time_slots")
