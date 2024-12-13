from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from .manager import CustomUserManager


class Profile(AbstractUser):
    ROLE_TYPES = [("Provider", "Provider"), ("User", "User"), ("Admin", "Admin")]
    role = models.CharField(max_length=20, choices=ROLE_TYPES, default=None, null=True)
    favorites = models.ManyToManyField(
        "self", related_name="favorited_by", blank=True, symmetrical=False
    )
    objects = CustomUserManager()

    username = models.CharField(max_length=20, unique=True)

    def clean(self):
        if len(self.username) > 20:
            raise ValidationError("Username cannot exceed 50 characters.")

    def __str__(self):
        return f"{self.get_username()} - {self.role}"


class Provider(models.Model):
    MENTAL_HEALTH_SPECIALIZATIONS = [
        ("Clinical Psychology", "Clinical Psychology"),
        ("Counseling Psychology", "Counseling Psychology"),
        ("Psychiatry", "Psychiatry"),
        ("Child and Adolescent Psychiatry", "Child and Adolescent Psychiatry"),
        ("Addiction Psychiatry", "Addiction Psychiatry"),
        ("Forensic Psychiatry", "Forensic Psychiatry"),
        ("Neuropsychology", "Neuropsychology"),
        ("Behavioral Therapy", "Behavioral Therapy"),
        ("Cognitive Behavioral Therapy", "Cognitive Behavioral Therapy"),
        ("Psychoanalysis", "Psychoanalysis"),
        # Add more mental health specializations as needed
    ]

    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="provider"
    )
    bio = models.TextField()
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=20)
    specialization = models.CharField(
        max_length=50, choices=MENTAL_HEALTH_SPECIALIZATIONS
    )
    is_activated = models.BooleanField(default=False)

    line1 = models.CharField(max_length=255, default="Unknown Address")
    line2 = models.CharField(max_length=255, blank=True, default="")
    city = models.CharField(max_length=100, default="Unknown City")
    state = models.CharField(max_length=100, default="Unknown State")
    pincode = models.CharField(max_length=10, default="000000")
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )

    def __str__(self):
        full_name = self.user.get_username()
        if len(full_name) > 20:
            full_name = full_name[:20] + "..."
        return f"{full_name} - {self.user.role} - {self.specialization}"


# this is the model for client users
class Client(models.Model):
    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="client"
    )
    bio = models.TextField()
    phone_number = models.CharField(max_length=20)
    user_label = models.CharField(max_length=20)

    def __str__(self):
        full_name = self.user.get_username()
        if len(full_name) > 20:
            full_name = full_name[:20] + "..."
        return f"{full_name} - {self.user.role} - {self.phone_number}"
