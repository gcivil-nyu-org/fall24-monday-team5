# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from appointments.models import Profile, TimeSlot, Appointment


User = get_user_model()

class AppointmentTests(TestCase):
    def setUp(self):
        # Create test users
        self.provider_user = User.objects.create_user(username="provider", password="pass")
        self.normal_user = User.objects.create_user(username="normal_user", password="pass")

        # Set up profiles
        self.provider_profile = Profile.objects.create(user=self.provider_user, role="Provider")
        self.normal_profile = Profile.objects.create(user=self.normal_user, role="User")

        # Set up test time slots
        self.time_slot = TimeSlot.objects.create(
            provider=self.provider_user,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True
        )

    def test_time_slots_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("appointments:time_slots"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/time_slots.html")

    def test_my_appointments_view_for_user(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("appointments:my_appointments"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/my_appointments.html")

    def test_my_appointments_view_for_provider(self):
        self.client.login(username="provider", password="pass")
        response = self.client.get(reverse("appointments:my_appointments"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/my_appointments.html")

    def test_cancel_appointment_view(self):
        # Book an appointment first
        self.client.login(username="normal_user", password="pass")
        appointment = Appointment.objects.create(user=self.normal_user, time_slot=self.time_slot)
        response = self.client.post(reverse("appointments:cancel_appointment", args=[appointment.id]))
        self.assertEqual(response.status_code, 302)

        # Ensure appointment is deleted and slot is available
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())
        self.time_slot.refresh_from_db()
        self.assertTrue(self.time_slot.is_available)

    def test_create_time_slot_view(self):
        self.client.login(username="provider", password="pass")
        start_time = timezone.now() + timedelta(days=3)
        end_time = start_time + timedelta(hours=1)
        response = self.client.post(reverse("appointments:create_time_slot"), {
            "form_type": "single",
            "start_time": start_time.strftime("%H:%M"),
            "end_time": end_time.strftime("%H:%M"),
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_slot_view(self):
        self.client.login(username="provider", password="pass")
        slot = TimeSlot.objects.create(
            provider=self.provider_user,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1),
            is_available=True
        )
        response = self.client.post(reverse("appointments:delete_slot", args=[slot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimeSlot.objects.filter(id=slot.id).exists())

    def test_browse_providers_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("appointments:browse_providers"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/browse_providers.html")

    def test_provider_detail_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("appointments:provider_detail", args=[self.provider_profile.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/provider_detail.html")
