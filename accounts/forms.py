from django import forms
from .models import Profile, Provider, Client

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email']

# 在 forms.py 中


class ProviderEditForm(forms.ModelForm):
    class Meta:
        model = Provider
        fields = ['phone_number', 'license_number', 'specialization', 'bio']
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'license_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control'}),
        }

class ClientEditForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['phone_number']