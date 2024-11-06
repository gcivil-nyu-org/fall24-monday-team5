from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile
from .forms import ProviderSignUpForm, UserSignUpForm


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
                "credentials": "Certified Professional",
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        profile = Profile.objects.get(user=user)
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
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.role, "User")
        self.assertEqual(user.first_name, "Regular")
        self.assertEqual(user.email, "user@example.com")

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
        User.objects.create_user(username="regularuser", password="password123")
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
