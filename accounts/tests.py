from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from accounts.models import Profile
from accounts.forms import ProfileEditForm

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

    # def test_profile_context_provider(self):
    #     self.user.role = "Provider"
    #     self.user.save()
    #     response = self.client.get(reverse("accounts:profile"))
    #     self.assertTrue(response.context["is_provider"])


class EditProfileViewTests(TestCase):
    def setUp(self):
        self.user = Profile.objects.create_user(
            username="testprovider",
            password="testpassword",
            role="Provider",
            email="<EMAIL>",
        )
        self.user = Profile.objects.create_user(
            username="testuser", password="testpassword", role="User", email="<EMAIL>"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_edit_profile_get(self):
        response = self.client.get(reverse("accounts:edit_profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/edit_profile.html")
        self.assertIsInstance(response.context["profile_form"], ProfileEditForm)

    def test_edit_profile_post_valid_data(self):
        response = self.client.post(
            reverse("accounts:edit_profile"),
            {
                "first_name": "NewFirst",
                "last_name": "NewLast",
                "email": "newemail@example.com",
            },
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "NewFirst")
        self.assertEqual(self.user.last_name, "NewLast")
        self.assertEqual(self.user.email, "newemail@example.com")

    # def test_edit_profile_provider_form(self):
    #     self.user.role = "Provider"
    #     self.user.save()
    #     response = self.client.get(reverse("accounts:edit_profile"))
    #     self.assertIsInstance(response.context["provider_form"], ProviderEditForm)


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
