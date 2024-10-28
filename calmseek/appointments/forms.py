from django import forms
from .models import Appointment, TimeSlot


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ["comments", "appointment_type"]

        # Adding some styling for the fields (optional)
        widgets = {
            "comments": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Enter any comments for the provider"}
            ),
            "appointment_type": forms.Select(),
        }


# Form for Providers to set Time Slots
class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ["start_time", "end_time", "is_available"]

        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "is_available": forms.CheckboxInput(),
        }
