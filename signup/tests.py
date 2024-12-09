from django.test import TestCase
from django.urls import reverse
from accounts.models import Client, Profile
from .forms import ProviderSignUpForm, UserSignUpForm


class SelectRoleViewTests(TestCase):
    def test_select_role_get(self):
        response = self.client.get(reverse("signup:select_role"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup/select_role.html")


class ProviderSignUpFormTests(TestCase):
    def test_provider_signup_form_valid_data(self):
        form = ProviderSignUpForm(
            data={
                "username": "provideruser",
                "first_name": "Provider",
                "last_name": "User",
                "email": "provider@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
                "credentials": "1234567890",
                "line1": "line 1",
                "line 2": "Apt A",
                "city": "Brooklyn",
                "state": "New York",
                "pincode": "11220",
                "bio": "bio",
                "phone_number": "99999999",
                "specialization": "Clinical Psychology",
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        profile = Profile.objects.get(id=user.id)
        self.assertEqual(profile.role, "Provider")
        self.assertEqual(user.first_name, "Provider")
        self.assertEqual(user.email, "provider@example.com")

    def test_provider_signup_form_missing_credentials(self):
        form = ProviderSignUpForm(
            data={
                "username": "provideruser",
                "first_name": "Provider",
                "last_name": "User",
                "email": "provider@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
                # Missing 'credentials'
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("credentials", form.errors)

    def test_provider_signup_form_password_mismatch(self):
        form = ProviderSignUpForm(
            data={
                "username": "provideruser",
                "first_name": "Provider",
                "last_name": "User",
                "email": "provider@example.com",
                "password1": "testpassword123",
                "password2": "wrongpassword",
                "credentials": "Certified Professional",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


class UserSignUpFormTests(TestCase):
    def test_user_signup_form_valid_data(self):
        form = UserSignUpForm(
            data={
                "username": "regularuser",
                "first_name": "Regular",
                "last_name": "User",
                "email": "user@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
                "phone_number": "99999999",
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        profile = Profile.objects.get(id=user.id)
        self.assertEqual(profile.role, "User")
        self.assertEqual(user.first_name, "Regular")
        self.assertEqual(user.email, "user@example.com")
        client = Client.objects.get(user=user)
        self.assertEqual(client.phone_number, "99999999")

    def test_user_signup_form_missing_email(self):
        form = UserSignUpForm(
            data={
                "username": "regularuser",
                "first_name": "Regular",
                "last_name": "User",
                # Missing 'email'
                "password1": "testpassword123",
                "password2": "testpassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_user_signup_form_password_mismatch(self):
        form = UserSignUpForm(
            data={
                "username": "regularuser",
                "first_name": "Regular",
                "last_name": "User",
                "email": "user@example.com",
                "password1": "testpassword123",
                "password2": "wrongpassword",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_user_signup_form_duplicate_username(self):
        Profile.objects.create_user(
            username="regularuser", password="password123", email="user@example.com"
        )
        form = UserSignUpForm(
            data={
                "username": "regularuser",
                "first_name": "Regular",
                "last_name": "User",
                "email": "user@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)


class ProviderSignUpViewTests(TestCase):
    def test_provider_signup_view_get(self):
        response = self.client.get(reverse("signup:signup_provider"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup/signup_provider.html")

    def test_provider_signup_view_post_missing_credentials(self):
        response = self.client.post(
            reverse("signup:signup_provider"),
            data={
                "username": "provideruser",
                "first_name": "Provider",
                "last_name": "User",
                "email": "provider@example.com",
                "password1": "testpassword123",
                "password2": "testpassword123",
                # Missing 'credentials'
            },
        )
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("credentials", form.errors)

    def test_provider_signup_view_get_request(self):
        response = self.client.get(reverse("signup:signup_provider"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup/signup_provider.html")


class UserSignUpViewTests(TestCase):
    def test_user_signup_view_get(self):
        response = self.client.get(reverse("signup:signup_user"))
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(form.is_bound)
        self.assertIsInstance(form, UserSignUpForm)
        self.assertTemplateUsed(response, "signup/signup_user.html")

    def test_user_signup_view_post_missing_email(self):
        response = self.client.post(
            reverse("signup:signup_user"),
            data={
                "username": "regularuser",
                "first_name": "Regular",
                "last_name": "User",
                "password1": "testpassword123",
                "password2": "testpassword123",
                # Missing 'email'
            },
        )
        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_user_signup_view_get_request(self):
        response = self.client.get(reverse("signup:signup_user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup/signup_user.html")
