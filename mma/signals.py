from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Balance

@receiver(post_save, sender=User)
def create_user_balance(sender, instance, created, **kwargs):
    if created:
        Balance.objects.create(agent=instance)
