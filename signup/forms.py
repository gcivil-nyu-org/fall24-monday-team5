from django import forms
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile, Provider


class ProviderSignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=255, required=True)
    credentials = forms.CharField(
        max_length=255, required=True, help_text="Enter your professional credentials"
    )

    # Address fields
    line1 = forms.CharField(max_length=255, required=True, label="Address Line 1")
    line2 = forms.CharField(max_length=255, required=False, label="Address Line 2")
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    specialization = forms.ChoiceField(
        choices=Provider.MENTAL_HEALTH_SPECIALIZATIONS, required=True
    )
    phone_number = forms.CharField(max_length=20, required=True)

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
            # Create the associated Provider object with address fields
            Provider.objects.create(
                user=user,
                # bio=self.cleaned_data.get("credentials"),
                # phone_number=self.cleaned_data["phone_number"],
                # =self.cleaned_data["credentials"],
                specialization=self.cleaned_data["specialization"],
                line1=self.cleaned_data["line1"],
                line2=self.cleaned_data.get("line2", ""),
                city=self.cleaned_data["city"],
                state=self.cleaned_data["state"],
                pincode=self.cleaned_data["pincode"],
            )
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
            # TODO here as we are creating a profile below code similarly we need to create a client
            # Profile.objects.create(
            #     user=user, role="User"
            # )  # the role 'User' is case sensitive (as of the moment)
        return user
