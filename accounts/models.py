from django.db import models
from django.contrib.auth.models import AbstractUser

from .manager import CustomUserManager


class Profile(AbstractUser):
    ROLE_TYPES = [("Provider", "Provider"), ("User", "User"), ("Admin", "Admin")]
    role = models.CharField(max_length=20, choices=ROLE_TYPES, default=None, null=True)
    favorites = models.ManyToManyField(
        "self", related_name="favorited_by", blank=True, symmetrical=False
    )
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.get_username()} - {self.role}"



class Provider(models.Model):
    MENTAL_HEALTH_SPECIALIZATIONS = [
        ('Clinical Psychology', 'Clinical Psychology'),
        ('Counseling Psychology', 'Counseling Psychology'),
        ('Psychiatry', 'Psychiatry'),
        ('Child and Adolescent Psychiatry', 'Child and Adolescent Psychiatry'),
        ('Addiction Psychiatry', 'Addiction Psychiatry'),
        ('Forensic Psychiatry', 'Forensic Psychiatry'),
        ('Neuropsychology', 'Neuropsychology'),
        ('Behavioral Therapy', 'Behavioral Therapy'),
        ('Cognitive Behavioral Therapy', 'Cognitive Behavioral Therapy'),
        ('Psychoanalysis', 'Psychoanalysis'),
        # Add more mental health specializations as needed
    ]

    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="provider"
    )
    bio = models.TextField()
    phone_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=20)
    specialization = models.CharField(
        max_length=50, choices=MENTAL_HEALTH_SPECIALIZATIONS)
    is_activated = models.BooleanField(default=False)
# this is the model for client users
class Client(models.Model):
    user = models.OneToOneField(
        Profile, on_delete=models.CASCADE, related_name="client"
    )
    bio = models.TextField()
    phone_number = models.CharField(max_length=20)
    user_label = models.CharField(max_length=20)
