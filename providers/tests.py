from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from appointments.models import TimeSlot
from accounts.models import Profile

User = get_user_model()


class ProviderViewsTest(TestCase):
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

    def test_create_time_slot_view(self):
        self.client.login(username="provider", password="pass")
        start_time = timezone.now() + timedelta(days=3)
        end_time = start_time + timedelta(hours=1)
        response = self.client.post(
            reverse("providers:create_time_slot"),
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
        response = self.client.post(reverse("providers:delete_slot", args=[slot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimeSlot.objects.filter(id=slot.id).exists())

    def test_browse_providers_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("providers:browse_providers"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "providers/browse_providers.html")

    def test_provider_detail_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(
            reverse("providers:provider_detail", args=[self.provider_user.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "providers/provider_detail.html")
