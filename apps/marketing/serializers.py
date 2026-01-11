from rest_framework import serializers
from apps.marketing.models import *


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "title", "message", "category", "recipient", "created_at"
        ]



class BlogSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    category = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Blog
        fields = [
            "id", "title", "slug", "category", "image", "exerpt", "content", "uploaded_by", "uploaded_at"
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        elif obj.image:
            return obj.image.url
        else:
            return None

