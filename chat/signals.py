# ChatProject/chat/signals.py
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        individual_id = str(uuid.uuid4())[:8]  # short unique id
        Profile.objects.create(user=instance, individual_id=individual_id)
