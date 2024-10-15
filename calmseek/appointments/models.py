from django.db import models
from django.contrib.auth.models import User

# Model for Time Slots set by the provider
class TimeSlot(models.Model):
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='provider_time_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.provider.username} - {self.start_time} to {self.end_time}"

# Model for Appointments booked by the user
class Appointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    comments = models.TextField(blank=True)
    APPOINTMENT_TYPES = [
        ('Checkup', 'Checkup'),
        ('Consultation', 'Consultation'),
        ('Emergency', 'Emergency'),
    ]
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    booked_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.user.username} on {self.time_slot.start_time}"
