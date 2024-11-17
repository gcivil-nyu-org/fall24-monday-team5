from django import forms
from .models import Profile, Provider, Client


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["first_name", "last_name", "email"]


class ProviderEditForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = [
            "phone_number",
            "license_number",
            "specialization",
            "bio",
            "line1",
            "line2",
            "city",
            "state",
            "pincode",
        ]
        widgets = {
            "specialization": forms.Select(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "license_number": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
            "line1": forms.TextInput(attrs={"class": "form-control"}),
            "line2": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "state": forms.TextInput(attrs={"class": "form-control"}),
            "pincode": forms.TextInput(attrs={"class": "form-control"}),
        }


class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["phone_number", "bio"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control"}),
        }


class PasswordResetRequestForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
