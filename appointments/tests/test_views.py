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
        self.provider_user = User.objects.create_user(
            username="provider", password="pass"
        )
        self.normal_user = User.objects.create_user(
            username="normal_user", password="pass"
        )

        # Set up profiles
        self.provider_profile = Profile.objects.create(
            user=self.provider_user, role="Provider"
        )
        self.normal_profile = Profile.objects.create(user=self.normal_user, role="User")

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

    def test_add_to_favorites(self):
        url = reverse("appointments:add_to_favorites", args=[self.provider_profile.id])
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("appointments:provider_detail", args=[self.provider_profile.id]),
        )

        # Check that provider is added to favorites
        self.assertIn(self.provider_profile, self.normal_profile.favorites.all())

    def test_view_favorite_providers(self):
        self.normal_profile.favorites.add(self.provider_profile)

        url = reverse("appointments:favorite_providers")
        response = self.client.get(url)

        # Confirm provider is in the favorites context
        self.assertIn(self.provider_profile, response.context["favorite_providers"])

    def test_remove_from_favorites(self):
        self.normal_profile.favorites.add(self.provider_profile)

        url = reverse(
            "appointments:remove_from_favorites", args=[self.provider_profile.id]
        )
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("appointments:provider_detail", args=[self.provider_profile.id]),
        )

        # Check that provider is removed from favorites
        self.assertNotIn(self.provider_profile, self.normal_profile.favorites.all())

    def test_delete_favorite_provider(self):
        self.normal_profile.favorites.add(self.provider_profile)

        url = reverse(
            "appointments:delete_favorite_provider", args=[self.provider_profile.id]
        )
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("appointments:favorite_providers"),
        )

        # Check that provider is removed from favorites
        self.assertNotIn(self.provider_profile, self.normal_profile.favorites.all())
