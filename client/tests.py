from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from appointments.models import TimeSlot
from accounts.models import Profile

User = get_user_model()


class ClientTests(TestCase):
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

    def test_add_to_favorites(self):
        url = reverse("client:add_to_favorites", args=[self.provider_user.id])
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("providers:provider_detail", args=[self.provider_user.id]),
        )

        # Check that provider is added to favorites
        self.assertIn(self.provider_user, self.normal_user.favorites.all())

    def test_view_favorite_providers(self):
        self.normal_user.favorites.add(self.provider_user)

        url = reverse("client:favorite_providers")
        response = self.client.get(url)

        # Confirm provider is in the favorites context
        self.assertIn(self.provider_user, response.context["favorite_providers"])

    def test_remove_from_favorites(self):
        self.normal_user.favorites.add(self.provider_user)

        url = reverse("client:remove_from_favorites", args=[self.provider_user.id])
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("providers:provider_detail", args=[self.provider_user.id]),
        )

        # Check that provider is removed from favorites
        self.assertNotIn(self.provider_user, self.normal_user.favorites.all())

    def test_delete_favorite_provider(self):
        self.normal_user.favorites.add(self.provider_user)

        url = reverse("client:delete_favorite_provider", args=[self.provider_user.id])
        response = self.client.post(url)

        # Confirm redirect to provider detail
        self.assertRedirects(
            response,
            reverse("client:favorite_providers"),
        )

        # Check that provider is removed from favorites
        self.assertNotIn(self.provider_user, self.normal_user.favorites.all())
