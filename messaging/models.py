from django.db import models
from accounts.models import Profile


class Contact(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="contacts")
    friend = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="friends"
    )
    is_friend = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} -> {self.friend.username}"


class Message(models.Model):
    sender = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sent_messages"
    )
    receiver = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="received_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"  # noqa: E501
