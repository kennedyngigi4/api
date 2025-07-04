import uuid
from django.db import models
from django.utils import timezone
# Create your models here.


class Notification(models.Model):

    CATEGORY_TYPES = [
        ( "personal", "Personal", ),
        ( "all", "All", ),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    category = models.CharField(max_length=255, choices=CATEGORY_TYPES, default="all")
    recipient = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



