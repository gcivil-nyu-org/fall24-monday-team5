from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from accounts.models import Profile


class ProviderSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=255, required=True)
    credentials = forms.CharField(
        max_length=255, required=True, help_text="Enter your professional credentials"
    )

    class Meta:
        model = Profile
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.role = "Provider"
        if commit:
            user.save()
            # Profile.objects.create(
            #     user=user, role="Provider"
            # )  # the role 'Provider' is case sensitive (as of the moment)
        return user


class UserSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=255, required=True)

    class Meta:
        model = Profile
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.role = "User"

        if commit:
            user.save()
            # Profile.objects.create(
            #     user=user, role="User"
            # )  # the role 'User' is case sensitive (as of the moment)
        return user
