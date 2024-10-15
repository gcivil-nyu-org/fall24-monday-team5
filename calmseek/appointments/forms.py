from django import forms
from .models import Appointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['comments', 'appointment_type']

        # Adding some styling for the fields (optional)
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter any comments for the provider'}),
            'appointment_type': forms.Select(),
        }
