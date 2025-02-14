# ChatProject/chat/models.py
from django.db import models
from django.contrib.auth.models import User

MESSAGE_STATUS = (
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('read', 'Read'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    individual_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='sent')

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username} at {self.timestamp}"
