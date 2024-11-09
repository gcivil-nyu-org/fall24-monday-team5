from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, ProviderEditForm, ClientEditForm

@login_required
def profile(request):
    user = request.user
    context = {
        "user": user,
        "is_provider": hasattr(user, 'provider'),
        "is_client": hasattr(user, 'client'),
    }
    return render(request, 'accounts/profile.html', context)



# 在 views.py 中

@login_required
def edit_profile(request):
    user = request.user

    # Determine if the user is a provider
    is_provider = user.role == 'Provider'

    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=user)
        provider_form = ProviderEditForm(request.POST, instance=user.provider) if is_provider else None

        # Save forms based on validity
        if profile_form.is_valid() and (not is_provider or provider_form.is_valid()):
            profile_form.save()
            if is_provider:
                provider_form.save()
            return redirect('accounts:profile')
    else:
        profile_form = ProfileEditForm(instance=user)
        provider_form = ProviderEditForm(instance=user.provider) if is_provider else None

    return render(request, 'accounts/edit_profile.html', {
        'profile_form': profile_form,
        'provider_form': provider_form,
        'is_provider': is_provider,
    })