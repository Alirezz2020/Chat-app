# ChatProject/chat/models.py
from django.core.exceptions import ValidationError
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

    def clean(self):
        if " " in self.individual_id:
            raise ValidationError("Individual ID cannot contain spaces.")

    def __str__(self):
        return f"{self.user.username}'s profile"
class GroupChat(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_groups')
    group_id = models.CharField(max_length=50, unique=True)
    group_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='group_images/', blank=True, null=True)
    members = models.ManyToManyField(User, through='GroupMembership', related_name='group_chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if " " in self.group_id:
            raise ValidationError("Group ID cannot contain spaces.")

    def __str__(self):
        return self.group_name

class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(GroupChat, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} joined {self.group.group_name}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    receiver = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='received_messages')
    group = models.ForeignKey(GroupChat, null=True, blank=True, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    attachment = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=MESSAGE_STATUS, default='sent')
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted = models.BooleanField(default=False)

    def delete_message(self):
        self.deleted = True
        self.content = "This message has been deleted"
        self.save()

    def edit_message(self, new_content):
        from django.utils import timezone
        self.content = new_content
        self.edited_at = timezone.now()
        self.save()

    def __str__(self):
        sender = self.sender.username if self.sender else 'System'
        return f"Msg from {sender} at {self.timestamp}"