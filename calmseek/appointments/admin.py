from django.contrib import admin
from .models import TimeSlot, Appointment, Profile

# Register your models here.
admin.site.register(TimeSlot)
admin.site.register(Appointment)
admin.site.register(Profile)