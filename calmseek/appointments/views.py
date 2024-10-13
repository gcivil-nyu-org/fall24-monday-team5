from django.shortcuts import render, get_object_or_404, redirect
from .models import TimeSlot, Appointment
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required

# View to display available time slots
@login_required
def time_slots(request):
    available_slots = TimeSlot.objects.filter(is_available=True)
    print("Time slots")
    return render(request, 'appointments/time_slots.html', {'time_slots': available_slots})

# View to handle appointment booking
@login_required
def book_appointment(request, slot_id):
    time_slot = get_object_or_404(TimeSlot, id=slot_id, is_available=True)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.time_slot = time_slot
            appointment.save()

            # Mark the time slot as no longer available
            time_slot.is_available = False
            time_slot.save()

            return redirect('appointments:appointment_success')

    else:
        form = AppointmentForm()

    return render(request, 'appointments/book_appointment.html', {'form': form, 'time_slot': time_slot})

@login_required
def appointment_success(request):
    return render(request, 'appointments/success.html')
