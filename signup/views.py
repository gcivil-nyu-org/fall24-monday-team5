from django.contrib.auth import login
from django.contrib import messages
from .forms import ProviderSignUpForm, UserSignUpForm
from accounts.models import Profile
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings
from .forms import PasswordResetRequestForm

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

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            try:
                profile = Profile.objects.get(username=username, email=email)
            except Profile.DoesNotExist:
                form.add_error(None, "User with the provided username and email does not exist.")
            else:
                token = default_token_generator.make_token(profile)
                uid = urlsafe_base64_encode(force_bytes(profile.pk))
                reset_url = request.build_absolute_uri(
                    reverse('signup:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                )
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                return redirect('signup:password_reset_sent')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'signup/password_reset_request.html', {'form': form})

def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        profile = Profile.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        profile = None

    if profile is not None and default_token_generator.check_token(profile, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            profile.set_password(new_password)
            profile.save()
            return redirect('signup:password_reset_complete')
        return render(request, 'signup/password_reset_confirm.html', {'validlink': True})
    else:
        return render(request, 'signup/password_reset_confirm.html', {'validlink': False})


def password_reset_sent(request):
    return render(request, 'signup/password_reset_sent.html')

def password_reset_complete(request):
    return render(request, 'signup/password_reset_complete.html')