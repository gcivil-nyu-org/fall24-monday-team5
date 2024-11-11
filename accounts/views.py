from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, ProviderEditForm, PasswordResetRequestForm
from accounts.models import Profile
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.conf import settings


@login_required
def profile(request):
    user = request.user
    context = {
        "user": user,
        "is_provider": hasattr(user, "provider"),
        "is_client": hasattr(user, "client"),
    }
    return render(request, "accounts/profile.html", context)


# 在 views.py 中


@login_required
def edit_profile(request):
    user = request.user

    # Determine if the user is a provider
    is_provider = user.role == "Provider"

    if request.method == "POST":
        profile_form = ProfileEditForm(request.POST, instance=user)
        provider_form = (
            ProviderEditForm(request.POST, instance=user.provider)
            if is_provider
            else None
        )

        # Save forms based on validity
        if profile_form.is_valid() and (not is_provider or provider_form.is_valid()):
            profile_form.save()
            if is_provider:
                provider_form.save()
            return redirect("accounts:profile")
    else:
        profile_form = ProfileEditForm(instance=user)
        provider_form = (
            ProviderEditForm(instance=user.provider) if is_provider else None
        )

    return render(
        request,
        "accounts/edit_profile.html",
        {
            "profile_form": profile_form,
            "provider_form": provider_form,
            "is_provider": is_provider,
        },
    )


def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            try:
                profile = Profile.objects.get(username=username, email=email)
            except Profile.DoesNotExist:
                form.add_error(
                    None, "User with the provided username and email does not exist."
                )
            else:
                token = default_token_generator.make_token(profile)
                uid = urlsafe_base64_encode(force_bytes(profile.pk))
                reset_url = request.build_absolute_uri(
                    reverse(
                        "accounts:password_reset_confirm",
                        kwargs={"uidb64": uid, "token": token},
                    )
                )
                send_mail(
                    subject="Password Reset Request",
                    message=f"Click the link to reset your password: {reset_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                )
                return redirect("accounts:password_reset_sent")
    else:
        form = PasswordResetRequestForm()
    return render(request, "accounts/password_reset_request.html", {"form": form})


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        profile = Profile.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Profile.DoesNotExist):
        profile = None

    if profile is not None and default_token_generator.check_token(profile, token):
        if request.method == "POST":
            new_password = request.POST.get("new_password")
            profile.set_password(new_password)
            profile.save()
            return redirect("accounts:password_reset_complete")
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": True}
        )
    else:
        return render(
            request, "accounts/password_reset_confirm.html", {"validlink": False}
        )


def password_reset_sent(request):
    return render(request, "accounts/password_reset_sent.html")


def password_reset_complete(request):
    return render(request, "accounts/password_reset_complete.html")
