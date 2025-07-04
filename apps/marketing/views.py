from django.shortcuts import render

from rest_framework import generics, views, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.marketing.models import *
from apps.marketing.serializers import *
# Create your views here.



class UserNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().order_by("-created_at")
    permission_classes = [ IsAuthenticated ]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(
            models.Q(category="all") |
            models.Q(recipient=user.uid)
        )
        return super().get_queryset()


