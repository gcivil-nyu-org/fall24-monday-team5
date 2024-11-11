from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from accounts.models import Profile
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from unittest.mock import patch


class ProfileViewsTestCase(TestCase):
    def setUp(self):
        # Create test profile
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

        self.client.login(username="normal_user", password="pass")

    def test_profile_view(self):
        self.client.login(username="normal_user", password="pass")
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertIn("user", response.context)
        self.assertIn("is_provider", response.context)
        self.assertIn("is_client", response.context)

    def test_profile_view_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_non_logged_in_user(self):
        self.client.logout()
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in_user(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_view_logged_in(self):
        response = self.client.get(reverse("accounts:edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")

    def test_edit_profile_post(self):
        data = {"username": "newusername", "first_name": "New", "last_name": "Name"}
        self.normal_user = Profile.objects.create_user(
            username="newusername",
            password="pass",
            role="User",
            email="testuser@example.com",
            first_name="New",
            last_name="Name",
        )
        self.client.login(username="newusername", password="pass")
        response = self.client.post(reverse("accounts:edit_profile"), data)
        self.assertEqual(response.status_code, 302)
        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.username, "newusername")
        self.assertEqual(self.normal_user.first_name, "New")
        self.assertEqual(self.normal_user.last_name, "Name")

    def test_edit_profile_post_invalid(self):
        data = {
            "username": "",  # Invalid username
            "first_name": "New",
            "last_name": "Name",
        }
        response = self.client.post(reverse("accounts:edit_profile"), data)
        self.assertEqual(response.status_code, 302)

    def test_edit_profile_post_missing_required_fields(self):
        data = {"username": "newuser"}
        response = self.client.post(reverse("accounts:edit_profile"), data)
        self.assertEqual(response.status_code, 302)

    @patch("django.core.mail.send_mail")
    def test_password_reset_request_post_valid(self, mock_send_mail):
        data = {"username": self.normal_user.username, "email": self.normal_user.email}
        response = self.client.post(reverse("accounts:password_reset_request"), data)
        self.assertEqual(
            response.status_code, 302
        )  # Redirect to password reset sent page
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password Reset Request", mail.outbox[0].subject)

    def test_password_reset_request_post_invalid_username(self):
        data = {"username": "wronguser", "email": "testuser@example.com"}
        response = self.client.post(reverse("accounts:password_reset_request"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "User with the provided username and email does not exist."
        )

    def test_password_reset_request_post_invalid_email(self):
        data = {"username": "testuser", "email": "wrongemail@example.com"}
        response = self.client.post(reverse("accounts:password_reset_request"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "User with the provided username and email does not exist."
        )

    def test_password_reset_confirm_valid(self):
        token = default_token_generator.make_token(self.normal_user)
        uid = urlsafe_base64_encode(force_bytes(self.normal_user.pk))
        url = reverse(
            "accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "validlink", 0)

    def test_password_reset_confirm_invalid(self):
        invalid_token = "invalidtoken"
        uid = urlsafe_base64_encode(force_bytes(self.normal_user.pk))
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": uid, "token": invalid_token},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "validlink", 0)

    def test_password_reset_complete_valid(self):
        new_password = "newpassword"
        data = {"new_password1": new_password, "new_password2": new_password}

        token = default_token_generator.make_token(self.normal_user)
        uid = urlsafe_base64_encode(force_bytes(self.normal_user.pk))
        url = reverse(
            "accounts:password_reset_confirm", kwargs={"uidb64": uid, "token": token}
        )
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.normal_user.refresh_from_db()
        self.assertFalse(self.normal_user.check_password(new_password))

    @patch("django.core.mail.send_mail")
    def test_password_reset_request_email_format_invalid(self, mock_send_mail):
        data = {"username": "testuser", "email": "testuser@example.com"}
        response = self.client.post(reverse("accounts:password_reset_request"), data)
        self.assertEqual(
            response.status_code, 200
        )  # Redirect to password reset sent page
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_complete_no_profile(self):
        response = self.client.get(reverse("accounts:password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_complete.html")

    def test_edit_profile_provider_role(self):
        self.provider_user.role = "Provider"
        self.provider_user.save()
        data = {
            "username": "provideruser",
            "first_name": "Provider",
            "last_name": "Name",
        }
        response = self.client.post(reverse("accounts:edit_profile"), data)
        self.assertEqual(response.status_code, 302)
        self.provider_user.refresh_from_db()
        self.assertEqual(self.provider_user.username, "provider")
        self.assertEqual(self.provider_user.first_name, "")

    @patch("django.core.mail.send_mail")
    def test_password_reset_request_multiple_users_same_email_invalid(
        self, mock_send_mail
    ):
        Profile.objects.create(
            username="anotheruser", email="testuser@example.com", password="password2"
        )
        data = {"username": "testuser", "email": "testuser@example.com"}
        response = self.client.post(reverse("accounts:password_reset_request"), data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(mail.outbox), 0
        )
