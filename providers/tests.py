from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from appointments.models import Profile, TimeSlot
from appointments.forms import TimeSlotForm

User = get_user_model()

class ProviderViewsTest(TestCase):
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

    def test_create_time_slot_view(self):
        self.client.login(username="provider", password="pass")
        start_time = timezone.now() + timedelta(days=3)
        end_time = start_time + timedelta(hours=1)
        response = self.client.post(
            reverse("appointments:create_time_slot"),
            {
                "form_type": "single",
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
            },
        )
        self.assertEqual(response.status_code, 200)

    def test_delete_slot_view(self):
        self.client.login(username="provider", password="pass")
        slot = TimeSlot.objects.create(
            provider=self.provider_user,
            start_time=timezone.now() + timedelta(days=2),
            end_time=timezone.now() + timedelta(days=2, hours=1),
            is_available=True,
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
        response = self.client.get(
            reverse("appointments:provider_detail", args=[self.provider_profile.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/provider_detail.html")
