from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from appointments.models import TimeSlot, Appointment
from accounts.models import Profile, Provider

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

        # Additional providers for filtering tests
        self.provider_specialist = Profile.objects.create_user(
            username="specialist_provider",
            password="pass",
            role="Provider",
            email="specialist@example.com",
        )
        Provider.objects.create(
            user=self.provider_specialist,
            bio="Experienced Therapist",
            phone_number="1234567890",
            license_number="LIC12345",
            specialization="Cognitive Behavioral Therapy",
            is_activated=True,
            line1="123 Therapy Lane",
            city="Therapyville",
            state="TX",
            pincode="12345",
        )

        self.provider_general = Profile.objects.create_user(
            username="general_provider",
            password="pass",
            role="Provider",
            email="general@example.com",
        )
        Provider.objects.create(
            user=self.provider_general,
            bio="Experienced General Provider",
            phone_number="0987654321",
            license_number="LIC54321",
            specialization="Clinical Psychology",
            is_activated=True,
            line1="456 Wellness St",
            city="Healthtown",
            state="CA",
            pincode="54321",
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

    def test_provider_detail_view_invalid_provider(self):
        self.client.login(username="normal_user", password="pass")
        invalid_provider_id = self.provider_user.id + 999
        response = self.client.get(
            reverse("providers:provider_detail", args=[invalid_provider_id])
        )
        self.assertEqual(response.status_code, 404)

    def test_delete_slot_with_appointment(self):
        self.client.login(username="provider", password="pass")
        appointment = Appointment.objects.create(
            user=self.normal_user,
            time_slot=self.time_slot,
            appointment_type="Checkup",
        )
        response = self.client.post(
            reverse("providers:delete_slot", args=[self.time_slot.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())
        self.assertFalse(TimeSlot.objects.filter(id=self.time_slot.id).exists())

    def test_browse_providers_with_specialization_filter(self):
        # Test filtering providers by specialization
        response = self.client.get(
            reverse("providers:browse_providers"),
            {"specialization": "Cognitive Behavioral Therapy"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.provider_specialist, response.context["page_obj"].object_list
        )
        self.assertNotIn(
            self.provider_general, response.context["page_obj"].object_list
        )

    def test_browse_providers_with_address_filter(self):
        # Test filtering providers by address
        response = self.client.get(
            reverse("providers:browse_providers"), {"address": "Therapyville"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.provider_specialist, response.context["page_obj"].object_list
        )
        self.assertNotIn(
            self.provider_general, response.context["page_obj"].object_list
        )

    def test_browse_providers_with_both_filters(self):
        # Test filtering providers by both specialization and address
        response = self.client.get(
            reverse("providers:browse_providers"),
            {
                "specialization": "Cognitive Behavioral Therapy",
                "address": "Therapyville",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            self.provider_specialist, response.context["page_obj"].object_list
        )
        self.assertNotIn(
            self.provider_general, response.context["page_obj"].object_list
        )

    def test_browse_providers_no_match_filters(self):
        # Test filtering with parameters that match no providers
        response = self.client.get(
            reverse("providers:browse_providers"),
            {"specialization": "Pediatric Psychiatry", "address": "Unknown City"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"].object_list), 0)

    def test_browse_providers_empty_filter(self):
        response = self.client.get(reverse("providers:browse_providers"))
        self.assertEqual(response.status_code, 200)
        providers = response.context["page_obj"].object_list
        self.assertIn(self.provider_user, providers)
        self.assertIn(self.provider_specialist, providers)
        self.assertIn(self.provider_general, providers)

    def test_create_time_slot_single_slot_invalid(self):
        self.client.login(username="provider", password="pass")
        response = self.client.post(
            reverse("providers:create_time_slot"),
            {
                "form_type": "single",
                "start_time": "",  # Missing start time
                "end_time": "",  # Missing end time
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")

    def test_create_time_slot_recurring(self):
        self.client.login(username="provider", password="pass")
        response = self.client.post(
            reverse("providers:create_time_slot"),
            {
                "form_type": "recurring",
                "start_time": "10:00",
                "end_time": "11:00",
                "repeat_days": ["Monday", "Wednesday"],
                "num_weeks": 2,
            },
        )
        self.assertEqual(response.status_code, 302)  # Should redirect
        time_slots = TimeSlot.objects.filter(provider=self.provider_user)
        self.assertEqual(time_slots.count(), 5)  # 2 days per week x 2 weeks

    def test_browse_providers_pagination(self):
        self.client.login(username="normal_user", password="pass")

        # Create additional providers to exceed one page
        for i in range(10):
            Profile.objects.create_user(
                username=f"provider_{i}",
                password="pass",
                role="Provider",
                email=f"provider_{i}@example.com",
            )

        response = self.client.get(reverse("providers:browse_providers"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_previous())

    def test_create_time_slot_unauthorized_access(self):
        response = self.client.get(reverse("providers:create_time_slot"))
        self.assertEqual(response.status_code, 302)  # Should redirect to error page

    def test_delete_slot_without_appointments(self):
        self.client.login(username="provider", password="pass")
        slot = TimeSlot.objects.create(
            provider=self.provider_user,
            start_time=timezone.now() + timedelta(days=3),
            end_time=timezone.now() + timedelta(days=3, hours=1),
            is_available=True,
        )
        response = self.client.post(reverse("providers:delete_slot", args=[slot.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimeSlot.objects.filter(id=slot.id).exists())

    def test_delete_invalid_slot(self):
        self.client.login(username="provider", password="pass")
        invalid_slot_id = 99999  # Non-existent ID
        response = self.client.post(
            reverse("providers:delete_slot", args=[invalid_slot_id])
        )
        self.assertEqual(response.status_code, 404)
