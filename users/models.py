from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
import io
from django.core.files.base import ContentFile
import logging

# Configure logging
logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, unique=True)
    house_number = models.CharField(max_length=50)
    business_location = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    profile_pic_thumbnail = models.ImageField(upload_to='profile_pics/thumbnails/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)  # Add this line

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

@receiver(post_save, sender=CustomUser)
def handle_profile_pic(sender, instance, **kwargs):
    if instance.profile_pic and not instance.profile_pic_thumbnail:
        logger.info(f'Profile picture uploaded for user: {instance.username}')

        try:
            image = Image.open(instance.profile_pic)
            max_size = (200, 200)
            image.thumbnail(max_size)

            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            buffer.seek(0)
            instance.profile_pic.save(
                instance.profile_pic.name,
                ContentFile(buffer.getvalue()),
                save=False
            )

            thumb_size = (100, 100)
            image.thumbnail(thumb_size)

            thumb_io = io.BytesIO()
            image.save(thumb_io, format='JPEG')
            thumb_file = ContentFile(thumb_io.getvalue(), 'thumb_' + instance.profile_pic.name)

            instance.profile_pic_thumbnail.save(thumb_file.name, thumb_file, save=False)
            logger.info(f'Thumbnail created for user: {instance.username}')

            instance.save(update_fields=['profile_pic_thumbnail'])

        except Exception as e:
            logger.error(f'Error processing profile picture for user {instance.username}: {e}')
