from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.models import Client, Profile, Provider
from accounts.forms import ClientEditForm, ProfileEditForm, ProviderEditForm

User = get_user_model()


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            username="testuser", password="testpassword", role="User", email="<EMAIL>"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_profile_view(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/profile.html")
        self.assertEqual(response.context["user"], self.user)


class EditProfileViewTests(TestCase):
    def setUp(self):
        # Create a provider user
        self.provider_user = Profile.objects.create_user(
            username="provider_user",
            password="password",
            role="Provider",
            email="provider@example.com",
        )
        self.provider = Provider.objects.create(user=self.provider_user)

        # Create a client user
        self.client_user = Profile.objects.create_user(
            username="client_user",
            password="password",
            role="Client",
            email="client@example.com",
        )
        self.clientu = Client.objects.create(user=self.client_user)

    def test_edit_profile_get_provider(self):
        self.client.login(username="provider_user", password="password")
        response = self.client.get(reverse("accounts:edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")
        self.assertIsInstance(response.context["profile_form"], ProfileEditForm)
        self.assertIsInstance(response.context["provider_form"], ProviderEditForm)
        self.assertIsNone(response.context["client_form"])
        self.assertTrue(response.context["is_provider"])

    def test_edit_profile_get_client(self):
        self.client.login(username="client_user", password="password")
        response = self.client.get(reverse("accounts:edit_profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")
        self.assertIsInstance(response.context["profile_form"], ProfileEditForm)
        self.assertIsNone(response.context["provider_form"])
        self.assertIsInstance(response.context["client_form"], ClientEditForm)
        self.assertFalse(response.context["is_provider"])

    # def test_edit_profile_post_provider_valid(self):
    #     self.client.login(username="provider_user", password="password")
    #     response = self.client.post(
    #         reverse("accounts:edit_profile"),
    #         data={
    #             "username": "updated_provider_user",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertRedirects(response, reverse("accounts:profile"))
    #     self.provider_user.refresh_from_db()
    #     self.provider.refresh_from_db()
    #     self.assertEqual(self.provider_user.username, "updated_provider_user")

    # def test_edit_profile_post_client_valid(self):
    #     self.client.login(username="client_user", password="password")
    #     response = self.client.post(
    #         reverse("accounts:edit_profile"),
    #         data={
    #             "username": "updated_client_user",
    #         },
    #     )

    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse("accounts:profile"))
    #     self.client_user.refresh_from_db()
    #     self.client.refresh_from_db()
    #     self.assertEqual(self.client_user.username, "updated_client_user")

    def test_edit_profile_post_invalid(self):
        self.client.login(username="provider_user", password="password")
        response = self.client.post(
            reverse("accounts:edit_profile"), data={"username": ""}
        )  # Missing required fields

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")


class PasswordResetRequestViewTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            username="testuser", email="user@example.com", password="password"
        )

    def test_password_reset_request_get(self):
        response = self.client.get(reverse("accounts:password_reset_request"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_request.html")

    def test_password_reset_request_post_valid(self):
        response = self.client.post(
            reverse("accounts:password_reset_request"),
            {"username": "testuser", "email": "user@example.com"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_sent"))

    def test_password_reset_request_post_invalid_user(self):
        response = self.client.post(
            reverse("accounts:password_reset_request"),
            {"username": "invaliduser", "email": "user@example.com"},
        )
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn(
            "User with the provided username and email does not exist.",
            form.non_field_errors(),
        )


class PasswordResetConfirmViewTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            username="testuser", email="user@example.com", password="password"
        )
        self.token = default_token_generator.make_token(self.user)
        self.uid = urlsafe_base64_encode(force_bytes(self.user.pk))

    def test_password_reset_confirm_get_valid_link(self):
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_confirm.html")
        self.assertTrue(response.context["validlink"])

    def test_password_reset_confirm_post_valid(self):
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": self.token},
        )
        response = self.client.post(url, {"new_password": "new_password123"})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password123"))
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))

    def test_password_reset_confirm_invalid_link(self):
        url = reverse(
            "accounts:password_reset_confirm",
            kwargs={"uidb64": self.uid, "token": "invalidtoken"},
        )
        response = self.client.get(url)
        self.assertFalse(response.context["validlink"])


class PasswordResetCompleteViewTests(TestCase):
    def test_password_reset_complete_view(self):
        response = self.client.get(reverse("accounts:password_reset_complete"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset_complete.html")
