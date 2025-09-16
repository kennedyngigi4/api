from django.db import models

# Create your models here.

class ConversationState(models.Model):
    phone  = models.CharField(max_length=30, unique=True)
    step = models.IntegerField(default=0)
    flow = models.CharField(max_length=50, null=True, blank=True)
    temp_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.phone} - step {self.step}"



