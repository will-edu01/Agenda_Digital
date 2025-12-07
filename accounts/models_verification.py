from django.db import models
from django.utils import timezone
import uuid

class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    token = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f"{self.email} - {self.code}"
