from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import calendar

from appointments.forms import TimeSlotForm
from appointments.models import Profile, TimeSlot


# Create your views here.
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
                return redirect("providers:create_time_slot")
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
                return redirect("providers:create_time_slot")
            else:
                # Handle missing data or validation errors
                error_message = "Please fill in all required fields."
                form = TimeSlotForm()
                current_slots = TimeSlot.objects.filter(provider=request.user)
                return render(
                    request,
                    "providers/create_time_slot.html",
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
        "providers/create_time_slot.html",
        {
            "form": form,
            "current_slots": current_slots,
        },
    )


@login_required
def browse_providers(request):
    # Query for all profiles with the role 'Provider'
    providers = Profile.objects.filter(role="Provider")
    return render(request, "providers/browse_providers.html", {"providers": providers})


@login_required
def provider_detail(request, provider_id):
    # Retrieve the provider's profile or return 404 if not found
    provider = get_object_or_404(Profile, id=provider_id, role="Provider")
    time_slots = TimeSlot.objects.filter(provider=provider.user)
    return render(
        request,
        "providers/provider_detail.html",
        {"provider": provider, "time_slots": time_slots},
    )
