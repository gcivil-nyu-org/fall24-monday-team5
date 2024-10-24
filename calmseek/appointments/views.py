from django.shortcuts import render, get_object_or_404, redirect
from .models import TimeSlot, Appointment
from .forms import AppointmentForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Appointment, TimeSlot
User = get_user_model()

# View to display available time slots by date and provider
@login_required
def time_slots(request):
    selected_provider_id = request.GET.get("provider")
    selected_date = request.GET.get("date")

    # Filter providers
    providers = User.objects.filter(is_staff=False)  # Assuming providers have 'is_staff' attribute set to True
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Filter by provider if selected
    if selected_provider_id:
        time_slots = time_slots.filter(provider_id=selected_provider_id)

    # Filter by date if selected
    if selected_date:
        selected_date_obj = parse_date(selected_date)
        if selected_date_obj:
            start_of_day = datetime.combine(selected_date_obj, datetime.min.time())
            end_of_day = datetime.combine(selected_date_obj, datetime.max.time())
            time_slots = time_slots.filter(start_time__range=(start_of_day, end_of_day))

    context = {
        'time_slots': time_slots,
        'providers': providers,
        'selected_provider_id': int(selected_provider_id) if selected_provider_id else None,
        'selected_date': selected_date,
    }
    return render(request, 'appointments/time_slots.html', context)

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

@login_required
def my_appointments(request):
    # Fetch all appointments for the logged-in user
    user_appointments = Appointment.objects.filter(user=request.user).select_related('time_slot')

    context = {
        'appointments': user_appointments
    }
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)

    if request.method == 'POST':
        # Mark the related time slot as available again
        time_slot = appointment.time_slot
        time_slot.is_available = True
        time_slot.save()

        # Delete the appointment
        appointment.delete()

        return HttpResponseRedirect(reverse('appointments:my_appointments'))

    return HttpResponseRedirect(reverse('appointments:my_appointments'))


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    return render(request, 'appointments/appointment_rescheduling.html', {'appointment': appointment})


@login_required
def reschedule_time_slots(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    selected_provider_id = request.GET.get("provider")
    selected_date = request.GET.get("date")

    # Filter providers
    providers = User.objects.filter(is_staff=False)  # Assuming providers have 'is_staff' attribute set to True
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Filter by provider if selected
    if selected_provider_id:
        time_slots = time_slots.filter(provider_id=selected_provider_id)

    # Filter by date if selected
    if selected_date:
        selected_date_obj = parse_date(selected_date)
        if selected_date_obj:
            start_of_day = datetime.combine(selected_date_obj, datetime.min.time())
            end_of_day = datetime.combine(selected_date_obj, datetime.max.time())
            time_slots = time_slots.filter(start_time__range=(start_of_day, end_of_day))

    context = {
        'time_slots': time_slots,
        'providers': providers,
        'selected_provider_id': int(selected_provider_id) if selected_provider_id else None,
        'selected_date': selected_date,
        'appointment': appointment,
    }

    return render(request, 'appointments/appointment_rescheduling.html', context)


@login_required
def update_appointment(request, appointment_id, slot_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, user=request.user)
    user = appointment.user
    new_time_slot = get_object_or_404(TimeSlot, id=slot_id, is_available=True)
    form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        old_time_slot = appointment.time_slot
        old_time_slot.is_available = True
        old_time_slot.save()
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.time_slot = new_time_slot
            appointment.save()

            # Mark the time slot as no longer available
            new_time_slot.is_available = False
            new_time_slot.save()

            return redirect('appointments:appointment_success')

    else:
        form = AppointmentForm(instance=appointment)

    context = {
        'time_slot': new_time_slot,
        'appointment': appointment,
        'form': form,
    }

    return render(request, 'appointments/update_appointment.html', context)
