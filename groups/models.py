from django.db import models
from django.utils.timezone import now
from accounts.models import Profile


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="created_groups"
    )
    members = models.ManyToManyField(Profile, related_name="group_members")
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="group_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)

    def __str__(self):
        return f"Message from {self.sender.username} in {self.group.name}"


class Invitation(models.Model):
    INVITATION_STATUS = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="invitations"
    )
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="invitations"
    )
    status = models.CharField(
        max_length=10, choices=INVITATION_STATUS, default="pending"
    )
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return f"Invitation from {self.group.created_by.username} to {self.user.username} for {self.group.name}"  # noqa: E501
