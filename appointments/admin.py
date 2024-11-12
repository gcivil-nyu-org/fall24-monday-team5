from django.contrib import admin
from .models import TimeSlot, Appointment

# Register your models here.
admin.site.register(TimeSlot)
admin.site.register(Appointment)
