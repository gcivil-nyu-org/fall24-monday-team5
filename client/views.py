from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from accounts.models import Profile


# Create your views here.
@login_required
def add_to_favorites(request, provider_id):
    provider = get_object_or_404(Profile, id=provider_id, role="Provider")
    user_profile = request.user.profile

    if provider in user_profile.favorites.all():
        messages.info(
            request, f"{provider.user.get_full_name()} is already in your favorites."
        )
    else:
        user_profile.favorites.add(provider)
        messages.success(
            request, f"Added {provider.user.get_full_name()} to your favorites."
        )

    return redirect("providers:provider_detail", provider_id=provider_id)


@login_required
def favorite_providers(request):
    favorite_providers = request.user.profile.favorites.all()
    return render(
        request,
        "client/favorite_providers.html",
        {"favorite_providers": favorite_providers},
    )


@login_required
def remove_from_favorites(request, provider_id):
    provider = get_object_or_404(Profile, id=provider_id, role="Provider")
    user_profile = request.user.profile
    user_profile.favorites.remove(provider)
    messages.success(
        request, f"Removed {provider.user.get_full_name()} from your favorites."
    )
    return redirect("providers:provider_detail", provider_id=provider_id)


def delete_favorite_provider(request, provider_id):
    provider = get_object_or_404(Profile, id=provider_id, role="Provider")
    user_profile = request.user.profile
    user_profile.favorites.remove(provider)
    messages.success(
        request, f"Removed {provider.user.get_full_name()} from your favorites."
    )
    return redirect("client:favorite_providers")
