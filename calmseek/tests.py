from django.test import TestCase
from django.urls import reverse
from accounts.models import Profile
from django.contrib.auth.models import AnonymousUser


class LoginViewTest(TestCase):
    def setUp(self):
        self.normal_user = Profile.objects.create_user(
            username="normal_user",
            password="pass",
            role="User",
            email="testuser@example.com",
        )
        self.login_url = reverse("login")
        self.time_slots_url = reverse("appointments:time_slots")
        self.logout_url = reverse("logout")

    def test_login_valid_user(self):
        # Test login with valid credentials
        response = self.client.post(
            self.login_url, {"username": "normal_user", "password": "pass"}
        )
        self.assertRedirects(response, reverse("appointments:time_slots"))
        user = self.client.get(reverse("appointments:time_slots"))
        self.assertEqual(user.status_code, 200)

    def test_login_invalid_user(self):
        # Test login with invalid credentials.
        response = self.client.post(
            self.login_url, {"username": "normal_user", "password": "wrongpassword"}
        )
        self.assertFormError(
            response,
            "form",
            None,
            "Please enter a correct username and password. Note that both fields may be case-sensitive.",  # noqa: E501
        )
        self.assertTemplateUsed(response, "registration/login.html")

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
