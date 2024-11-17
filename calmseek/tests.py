from django.test import TestCase
from django.urls import reverse
from accounts.models import Client, Profile
from django.contrib.auth.models import AnonymousUser


class LoginViewTest(TestCase):
    def setUp(self):
        self.normal_user = Profile.objects.create_user(
            username="normal_user",
            password="pass",
            role="User",
            email="testuser@example.com",
        )
        self.normal_client = Client.objects.create(user=self.normal_user)
        self.login_url = reverse("login")
        self.home_url = reverse("home")
        self.time_slots_url = reverse("appointments:time_slots")
        self.logout_url = reverse("logout")

    def test_login_valid_user(self):
        # Test login with valid credentials
        response = self.client.post(
            self.login_url, {"username": "normal_user", "password": "pass"}, follow=True
        )
        self.assertRedirects(response, reverse("accounts:client_dashboard"))
        user = self.client.get(reverse("accounts:client_dashboard"))
        self.assertEqual(user.status_code, 200)

    def test_login_invalid_user(self):
        # Test login with invalid credentials.
        response = self.client.post(
            self.login_url, {"username": "normal_user", "password": "wrongpassword"}
        )
        # Ensure the response re-renders the login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/login.html")

        # Check for form errors
        form = response.context.get("form")  # Get the form from the response context
        self.assertIsNotNone(form)  # Ensure the form exists
        self.assertFormError(
            form,
            None,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.", # noqa: E501
        )

    def test_access_protected_page_without_login(self):
        # Test that trying to access a protected page without logging in redirects.
        response = self.client.get(self.time_slots_url, follow=True)
        self.assertRedirects(response, f"{self.login_url}?next={self.time_slots_url}")
        self.assertTemplateUsed(response, "registration/login.html")

    def test_logout(self):
        # Test logout functionality.
        self.client.login(username="normal_user", password="pass")
        # Log out
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)
        user = response.wsgi_request.user
        self.assertTrue(isinstance(user, AnonymousUser))
