from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)
