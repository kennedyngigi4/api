from rest_framework import serializers
from apps.marketing.models import *


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "category", "recipient", "created_at"
        ]

