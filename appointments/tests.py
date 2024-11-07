# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from appointments.models import TimeSlot, Appointment
from accounts.models import Profile


User = get_user_model()


class AppointmentTests(TestCase):
    def setUp(self):
        # Create test users
        self.provider_user = Profile.objects.create_user(
            username="provider",
            password="pass",
            role="Provider",
            email="testprovider@example.com",
        )
        self.normal_user = Profile.objects.create_user(
            username="normal_user",
            password="pass",
            role="User",
            email="testuser@example.com",
        )

        # Set up test time slots
        self.time_slot = TimeSlot.objects.create(
            provider=self.provider_user,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True,
        )

        # Login the normal user for certain tests
        self.client.login(username="normal_user", password="pass")

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
        appointment = Appointment.objects.create(
            user=self.normal_user, time_slot=self.time_slot
        )
        response = self.client.post(
            reverse("appointments:cancel_appointment", args=[appointment.id])
        )
        self.assertEqual(response.status_code, 302)

        # Ensure appointment is deleted and slot is available
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())
        self.time_slot.refresh_from_db()
        self.assertTrue(self.time_slot.is_available)
