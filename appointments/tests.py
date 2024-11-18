# Create your tests here.
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
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

    def test_appointment_success_view(self):
        response = self.client.get(reverse("appointments:appointment_success"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/success.html")

    def test_reschedule_time_slots_view(self):
        # First, book an appointment to reschedule
        appointment = Appointment.objects.create(
            user=self.normal_user, time_slot=self.time_slot
        )

        # Make a GET request to load rescheduling options
        response = self.client.post(
            reverse("appointments:reschedule_time_slots"),
            {"appointment_id": appointment.id},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/appointment_rescheduling.html")
        self.assertContains(
            response, "time_slots"
        )  # Context should contain available time slots

    def test_reschedule_appointment_not_provider_view(self):
        # User should not be able to reschedule to unavailable time slot
        self.time_slot.is_available = False
        self.time_slot.save()

        response = self.client.get(reverse("appointments:reschedule_time_slots"))
        self.assertEqual(
            response.status_code, 404
        )  # Should show not found as slot is unavailable


class TimeSlotModelTests(TestCase):
    def setUp(self):
        # Create a provider profile for the test
        self.provider = Profile.objects.create_user(
            username="provider_user",
            password="provider_pass",
            role="Provider",
            email="provider@example.com",
        )

    def test_create_time_slot(self):
        # Create a time slot for the provider
        time_slot = TimeSlot.objects.create(
            provider=self.provider,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True,
        )

        # Check if the time slot is created correctly
        self.assertEqual(time_slot.provider, self.provider)
        self.assertTrue(time_slot.is_available)

    def test_time_slot_str_method(self):
        # Create a time slot and test the __str__ method
        time_slot = TimeSlot.objects.create(
            provider=self.provider,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True,
        )
        expected_str = (
            f"{self.provider.username} - {time_slot.start_time} to {time_slot.end_time}"
        )
        self.assertEqual(str(time_slot), expected_str)

    def test_time_slot_availability(self):
        # Create and update the time slot to check availability
        time_slot = TimeSlot.objects.create(
            provider=self.provider,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True,
        )
        time_slot.is_available = False
        time_slot.save()

        # Ensure the availability has been updated
        self.assertFalse(time_slot.is_available)


class AppointmentModelTests(TestCase):
    def setUp(self):
        # Create test provider and user profiles
        self.provider = Profile.objects.create_user(
            username="provider_user",
            password="provider_pass",
            role="Provider",
            email="provider@example.com",
        )
        self.user = Profile.objects.create_user(
            username="normal_user",
            password="user_pass",
            role="User",
            email="user@example.com",
        )

        # Set up a time slot for the provider
        self.time_slot = TimeSlot.objects.create(
            provider=self.provider,
            start_time=timezone.now() + timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1, hours=1),
            is_available=True,
        )

    def test_create_appointment(self):
        # Create an appointment for the user
        appointment = Appointment.objects.create(
            user=self.user,
            time_slot=self.time_slot,
            comments="Looking forward to it",
            appointment_type="Consultation",
        )

        # Check if the appointment is created and linked correctly
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.time_slot, self.time_slot)
        self.assertEqual(appointment.comments, "Looking forward to it")
        self.assertEqual(appointment.appointment_type, "Consultation")
        self.assertIsNotNone(appointment.booked_on)

    def test_appointment_str_method(self):
        # Create an appointment and test the __str__ method
        appointment = Appointment.objects.create(
            user=self.user,
            time_slot=self.time_slot,
            comments="Urgent appointment",
            appointment_type="Emergency",
        )
        expected_str = (
            f"Appointment for {self.user.username} on {self.time_slot.start_time}"
        )
        self.assertEqual(str(appointment), expected_str)

    def test_time_slot_marked_unavailable_on_appointment(self):
        # Create an appointment and ensure the time slot is marked as unavailable
        appointment = Appointment.objects.create(
            user=self.user,
            time_slot=self.time_slot,
            comments="Booking appointment",
            appointment_type="Checkup",
        )
        appointment.time_slot.is_available = False
        appointment.time_slot.save()

        # Check if time slot is correctly updated
        self.assertFalse(appointment.time_slot.is_available)


class BookAppointmentViewTest(TestCase):
    def setUp(self):
        # Create a user and a provider
        self.user = Profile.objects.create_user(
            username="user", password="password", role="User", email="user@example.com"
        )
        self.provider = Profile.objects.create_user(
            username="provider",
            password="password",
            role="Provider",
            email="provider@example.com",
        )

        # Create a time slot
        self.time_slot = TimeSlot.objects.create(
            provider=self.provider,
            start_time="2024-11-19 10:00",
            end_time="2024-11-19 11:00",
            is_available=True,
        )

    def test_redirect_if_provider(self):
        # Log in as a provider
        self.client.login(username="provider", password="password")

        response = self.client.get(reverse("appointments:book_appointment"))

        # Check if provider is redirected to their dashboard
        self.assertRedirects(response, reverse("appointments:time_slots"))

    def test_invalid_form_submission(self):
        # Log in as a user
        self.client.login(username="user", password="password")

        # Attempt to book an appointment with invalid data
        response = self.client.post(
            reverse("appointments:book_appointment"), {"time_slot": self.time_slot.id}
        )

        # Ensure the form is displayed again with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointments/book_appointment.html")
        self.assertTrue(response.context["form"].errors)

    def test_valid_appointment_booking(self):
        # Log in as a user
        self.client.login(username="user", password="password")

        # Book an appointment with valid data
        response = self.client.post(
            reverse("appointments:book_appointment"),
            {"time_slot": self.time_slot.id, "appointment_type": "Consultation"},
        )

        # Check if the user is redirected to success page
        self.assertRedirects(response, reverse("appointments:appointment_success"))

        # Check if the appointment is created
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.first()
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.time_slot, self.time_slot)

        # Ensure the time slot is marked unavailable
        self.time_slot.refresh_from_db()
        self.assertFalse(self.time_slot.is_available)


class UpdateAppointmentViewTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = Profile.objects.create_user(
            username="testuser", password="password", email="test@example"
        )
        self.provider = Profile.objects.create_user(
            username="provider", password="password", email="provider@example"
        )

        # Create initial time slots
        self.time_slot1 = TimeSlot.objects.create(
            id=1,
            provider=self.provider,
            start_time=datetime(2024, 12, 1, 10, 0),
            end_time=datetime(2024, 12, 1, 11, 0),
            is_available=True,
        )
        self.time_slot2 = TimeSlot.objects.create(
            id=2,
            provider=self.provider,
            start_time=datetime(2024, 12, 1, 11, 0),
            end_time=datetime(2024, 12, 1, 12, 0),
            is_available=True,
        )

        # Create an appointment
        self.appointment = Appointment.objects.create(
            id=1,
            user=self.user,
            time_slot=self.time_slot1,
            appointment_type="Consultation",
        )

        # Login the user
        self.client.login(username="testuser", password="password")

    def test_update_appointment_successful(self):
        """Test that updating an appointment with a valid form and available time slot works."""
        response = self.client.post(
            reverse("appointments:update_appointment"),
            {
                "appointment_id": self.appointment.id,
                "time_slot": self.time_slot2.id,
                "appointment_type": "Checkup",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("appointments:appointment_success"))

        # Verify the appointment was updated
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.time_slot, self.time_slot2)
        self.assertEqual(self.appointment.appointment_type, "Checkup")

        # Verify the old time slot is available and the new one is not
        self.time_slot1.refresh_from_db()
        self.assertTrue(self.time_slot1.is_available)
        self.time_slot2.refresh_from_db()
        self.assertFalse(self.time_slot2.is_available)

    def test_update_appointment_invalid_time_slot(self):
        """Test that updating with an unavailable time slot does not work."""
        self.time_slot2.is_available = False
        self.time_slot2.save()

        response = self.client.post(
            reverse("appointments:update_appointment"),
            {
                "appointment_id": self.appointment.id,
                "time_slot": self.time_slot2.id,
                "appointment_type": "Follow-up",
            },
        )

        self.assertEqual(response.status_code, 404)  # New time slot is not available

    def test_update_appointment_invalid_form(self):
        """Test that submitting an invalid form does not update the appointment."""
        response = self.client.post(
            reverse("appointments:update_appointment"),
            {
                "appointment_id": self.appointment.id,
                "time_slot": self.time_slot2.id,
                "appointment_type": "",  # Invalid data
            },
        )
        self.assertEqual(response.status_code, 200)  # Renders form with errors

        # Verify the appointment remains unchanged
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.time_slot, self.time_slot1)
        self.assertNotEqual(self.appointment.appointment_type, "")

    def test_update_appointment_invalid_appointment_id(self):
        """Test that updating with an invalid appointment ID returns a 404 error."""
        response = self.client.post(
            reverse("appointments:update_appointment"),
            {
                "appointment_id": 9999,  # Non-existent appointment
                "time_slot": self.time_slot2.id,
                "appointment_type": "Follow-up",
            },
        )
        self.assertEqual(response.status_code, 404)
