from django.contrib.auth import get_user_model
from django.db.models import Subquery
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_date
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from forms import AppointmentForm, TimeSlotForm
from models import Appointment, TimeSlot, Profile
import calendar

User = get_user_model()


# View to display available time slots by date and provider
@login_required
def time_slots(request):
    selected_provider_id = request.GET.get("provider")
    selected_date = request.GET.get("date")

    # Filter providers based on Profile role 'Provider'
    # providers = Profile.objects.filter(role='Provider').select_related('user')
    provider_user_ids = Profile.objects.filter(role="Provider").values("user_id")
    providers = User.objects.filter(id__in=Subquery(provider_user_ids))

    # Filter available time slots
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Filter by provider if selected
    if selected_provider_id:
        time_slots = time_slots.filter(provider__id=selected_provider_id)

    # Filter by date if selected
    if selected_date:
        selected_date_obj = parse_date(selected_date)
        if selected_date_obj:
            start_of_day = datetime.combine(selected_date_obj, datetime.min.time())
            end_of_day = datetime.combine(selected_date_obj, datetime.max.time())
            time_slots = time_slots.filter(start_time__range=(start_of_day, end_of_day))

    context = {
        "time_slots": time_slots,
        "providers": providers,
        "selected_provider_id": (
            int(selected_provider_id) if selected_provider_id else None
        ),
        "selected_date": selected_date,
    }
    return render(request, "appointments/time_slots.html", context)


# View to handle appointment booking
@login_required
def book_appointment(request, slot_id):
    # Check if the logged-in user is a 'Provider'
    profile = Profile.objects.get(user=request.user)
    if profile.role == "Provider":
        return redirect(
            "appointments:provider_dashboard"
        )  # Redirect provider to their dashboard

    # Proceed with appointment booking if user is not a 'Provider'
    time_slot = get_object_or_404(TimeSlot, id=slot_id, is_available=True)

    if request.method == "POST":
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.time_slot = time_slot
            appointment.save()

            # Mark the time slot as no longer available
            time_slot.is_available = False
            time_slot.save()

            return redirect("appointments:appointment_success")

    else:
        form = AppointmentForm()

    return render(
        request,
        "appointments/book_appointment.html",
        {"form": form, "time_slot": time_slot},
    )


@login_required
def appointment_success(request):
    return render(request, "appointments/success.html")


@login_required
def provider_dashboard(request):
    if not request.user.is_staff:  # Check if the user is a provider
        return redirect("appointments:book_appointment")

    # Fetch time slots associated with the logged-in provider
    time_slots = TimeSlot.objects.filter(provider=request.user)

    return render(
        request, "appointments/provider_dashboard.html", {"time_slots": time_slots}
    )


@login_required
def my_appointments(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == "Provider":
        # Provider sees all appointments related to their time slots
        provider_appointments = Appointment.objects.filter(
            time_slot__provider=request.user
        ).select_related("time_slot")
        context = {"appointments": provider_appointments}
    else:
        # Normal users see only their own appointments
        user_appointments = Appointment.objects.filter(
            user=request.user
        ).select_related("time_slot")
        context = {"appointments": user_appointments}

    return render(request, "appointments/my_appointments.html", context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    # Allow normal users to cancel their own appointments
    # Allow providers to cancel appointments related to their time slots
    if (
        appointment.user == request.user
        or appointment.time_slot.provider == request.user
    ):
        if request.method == "POST":
            # Mark the related time slot as available again
            time_slot = appointment.time_slot
            time_slot.is_available = True
            time_slot.save()

            # Delete the appointment
            appointment.delete()

            return HttpResponseRedirect(reverse("appointments:my_appointments"))

    return HttpResponseRedirect(reverse("appointments:my_appointments"))


@login_required
def reschedule_time_slots(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    profile = Profile.objects.get(user=request.user)
    selected_provider_id = 0
    providers = get_user_model()
    if profile.role == "User":
        selected_provider_id = request.GET.get("provider")
        # Filter providers based on Profile role 'Provider'
        # providers = Profile.objects.filter(role='Provider').select_related('user')
        provider_user_ids = Profile.objects.filter(role="Provider").values("user_id")
        providers = User.objects.filter(id__in=Subquery(provider_user_ids))
    if profile.role == "Provider":
        selected_provider_id = appointment.time_slot.provider.id
        providers = User.objects.filter(id=selected_provider_id)

    selected_date = request.GET.get("date")

    # Filter available time slots
    time_slots = TimeSlot.objects.filter(is_available=True)

    # Filter by provider if selected
    if selected_provider_id:
        time_slots = time_slots.filter(provider__id=selected_provider_id)

    # Filter by date if selected
    if selected_date:
        selected_date_obj = parse_date(selected_date)
        if selected_date_obj:
            start_of_day = datetime.combine(selected_date_obj, datetime.min.time())
            end_of_day = datetime.combine(selected_date_obj, datetime.max.time())
            time_slots = time_slots.filter(start_time__range=(start_of_day, end_of_day))

    context = {
        "time_slots": time_slots,
        "providers": providers,
        "selected_provider_id": (
            int(selected_provider_id) if selected_provider_id else None
        ),
        "selected_date": selected_date,
        "appointment": appointment,
    }

    return render(request, "appointments/appointment_rescheduling.html", context)


@login_required
def update_appointment(request, appointment_id, slot_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    original_user = appointment.user
    new_time_slot = get_object_or_404(TimeSlot, id=slot_id, is_available=True)
    form = AppointmentForm()
    print(request.method)

    if request.method == "POST":
        form = AppointmentForm(request.POST, instance=appointment)
        old_time_slot = appointment.time_slot
        old_time_slot.is_available = True
        old_time_slot.save()
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = original_user
            appointment.time_slot = new_time_slot
            appointment.save()

            # Mark the time slot as no longer available
            new_time_slot.is_available = False
            new_time_slot.save()

            return redirect("appointments:appointment_success")

    else:
        form = AppointmentForm(instance=appointment)

    context = {
        "time_slot": new_time_slot,
        "appointment": appointment,
        "form": form,
    }

    return render(request, "appointments/update_appointment.html", context)


@login_required
def dashboard(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # Check if the user is a provider
    if profile.role == "Provider":
        # Providers can view their own time slots
        time_slots = TimeSlot.objects.filter(provider=user)
        appointments = Appointment.objects.filter(time_slot__provider=user)
    else:
        # Users can view all providers to book an appointment
        time_slots = TimeSlot.objects.all()  # Or filter based on user choice
        appointments = Appointment.objects.filter(user=user)

    context = {
        "is_provider": profile.role == "Provider",
        "time_slots": time_slots,
        "appointments": appointments,
    }
    return render(request, "appointments/dashboard.html", context)


@login_required
def create_time_slot(request):
    user = request.user
    profile = Profile.objects.get(user=user)

    # Ensure only Providers can access this view
    if profile.role != "Provider":
        return redirect("appointments:book_appointment")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        # Single Slot Creation
        if form_type == "single":
            form = TimeSlotForm(request.POST)
            if form.is_valid():
                time_slot = form.save(commit=False)
                time_slot.provider = request.user
                time_slot.is_available = True  # Automatically set to available
                time_slot.save()
                # Refresh the page after saving
                return redirect("appointments:create_time_slot")
            else:
                # Handle form errors (optional)
                pass

        # Recurring Slot Creation
        elif form_type == "recurring":
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            selected_days = request.POST.getlist("repeat_days")
            num_weeks = int(request.POST.get("num_weeks", 1))

            # Validate required fields
            if start_time_str and end_time_str and selected_days:
                start_time = datetime.strptime(start_time_str, "%H:%M").time()
                end_time = datetime.strptime(end_time_str, "%H:%M").time()

                today = timezone.now().date()

                for week in range(num_weeks):
                    for day in selected_days:
                        weekday_index = list(calendar.day_name).index(day)
                        days_until_next = (weekday_index - today.weekday()) % 7
                        slot_date = today + timedelta(days=days_until_next + week * 7)

                        # Create each recurring slot
                        TimeSlot.objects.create(
                            provider=request.user,
                            start_time=timezone.make_aware(
                                datetime.combine(slot_date, start_time)
                            ),
                            end_time=timezone.make_aware(
                                datetime.combine(slot_date, end_time)
                            ),
                            is_available=True,  # Automatically set to available
                        )
                # Refresh the page after saving
                return redirect("appointments:create_time_slot")
            else:
                # Handle missing data or validation errors
                error_message = "Please fill in all required fields."
                form = TimeSlotForm()
                current_slots = TimeSlot.objects.filter(provider=request.user)
                return render(
                    request,
                    "appointments/create_time_slot.html",
                    {
                        "form": form,
                        "current_slots": current_slots,
                        "error_message": error_message,
                    },
                )

    else:
        form = TimeSlotForm()

    # Fetch current slots for display
    current_slots = TimeSlot.objects.filter(provider=request.user)
    return render(
        request,
        "appointments/create_time_slot.html",
        {
            "form": form,
            "current_slots": current_slots,
        },
    )


@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)

    # Check if the slot is available
    if not slot.is_available:
        # If the slot is not available, find and delete any associated appointments
        associated_appointments = Appointment.objects.filter(time_slot=slot)
        associated_appointments.delete()
        messages.warning(
            request, "The slot had appointments that have now been removed."
        )

    # Delete the slot
    slot.delete()
    messages.success(request, "Time slot deleted successfully.")
    return redirect("appointments:create_time_slot")
