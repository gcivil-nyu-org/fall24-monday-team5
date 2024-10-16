from django.shortcuts import render, get_object_or_404, redirect
from .models import TimeSlot, Appointment
from .forms import AppointmentForm, TimeSlotForm
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date

User = get_user_model()

# View to display available time slots by date and provider
@login_required
def time_slots(request):
    selected_provider_id = request.GET.get("provider")
    selected_date = request.GET.get("date")

    # Filter providers
    providers = User.objects.filter(is_staff=True)  # Assuming providers have 'is_staff' attribute set to True
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Filter by provider if selected
    if selected_provider_id:
        time_slots = time_slots.filter(provider__id=selected_provider_id, provider__is_staff=True)
    
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
def create_time_slot(request):
    if not request.user.is_staff:  # Assuming providers have 'is_staff' set to True
        return redirect('home')  # Redirect non-providers to home or appropriate page

    if request.method == 'POST':
        form = TimeSlotForm(request.POST)
        if form.is_valid():
            time_slot = form.save(commit=False)
            time_slot.provider = request.user  # Set the provider to the logged-in user
            time_slot.save()
            return redirect('appointments:provider_dashboard')  # Redirect to provider's dashboard
    else:
        form = TimeSlotForm()

    return render(request, 'appointments/create_time_slot.html', {'form': form})

@login_required
def provider_dashboard(request):
    if not request.user.is_staff:  # Check if the user is a provider
        return redirect('home')

    # Fetch time slots associated with the logged-in provider
    time_slots = TimeSlot.objects.filter(provider=request.user)

    return render(request, 'appointments/provider_dashboard.html', {'time_slots': time_slots})

