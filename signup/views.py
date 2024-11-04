from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import login
from django.contrib import messages
from .forms import ProviderSignUpForm, UserSignUpForm


def select_role(request):
    if request.method == "POST":
        role = request.POST.get("role")
        if role == "provider":
            return redirect(reverse("signup/signup_provider"))
        elif role == "user":
            return redirect(reverse("signup/signup_user"))
    return render(request, "signup/select_role.html")


def signup_provider(request):
    if request.method == "POST":
        form = ProviderSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Provider account created successfully!")
            return redirect("/appointments/time_slots")
    else:
        form = ProviderSignUpForm()
    return render(request, "signup/signup_provider.html", {"form": form})


def signup_user(request):
    if request.method == "POST":
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "User account created successfully!")
            return redirect("/appointments/time_slots")
    else:
        form = UserSignUpForm()
    return render(request, "signup/signup_user.html", {"form": form})
