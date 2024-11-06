from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser

from .manager import CustomUserManager


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    ROLE_TYPES = [("Provider", "Provider"), ("User", "User"), ("Admin", "Admin")]
    role = models.CharField(max_length=20, choices=ROLE_TYPES, default=None)
    favorites = models.ManyToManyField(
        "self", related_name="favorited_by", symmetrical=False, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"


# class Profile(AbstractUser):
#     ROLE_TYPES = [
#         ('Provider', 'Provider'),
#         ('User', 'User'),
#         ('Admin', 'Admin')
#     ]
#     role = models.CharField(max_length=20, choices=ROLE_TYPES, default=None, null=True)
#     objects = CustomUserManager()

#     def __str__(self):
#         return f"{self.get_username()} - {self.role}"

# this model is for the providers
# class Provider(models.Model):
#     user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='provider')
#     bio = models.TextField()
#     phone_number = models.CharField(max_length=20)
#     license_number = models.CharField(max_length=20)
#     specialization = models.CharField(max_length=20)
#     is_activated = models.BooleanField(default=False)

# # this is the model for client users
# class Client(models.Model):
#     user = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='client')
#     bio = models.TextField()
#     phone_number = models.CharField(max_length=20)
#     user_label = models.CharField(max_length=20)
