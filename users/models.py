from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13, unique=True, validators=[
        RegexValidator(regex=r'^\+260\d{9}$', message="Phone number must start with +260 and be 13 characters long.")
    ])
    house_number = models.CharField(max_length=50)
    business_location = models.CharField(max_length=255)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.username