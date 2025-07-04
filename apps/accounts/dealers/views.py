from django.shortcuts import render, get_object_or_404

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, JSONParser, FormParser

from apps.accounts.models import *
from apps.accounts.serializers import *
from apps.accounts.permissions import *



class BusinessUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [ IsAuthenticated ]
    serializer_class = BusinessSerializer
    queryset = UserBusiness.objects.all()
    parser_classes = [ MultiPartParser, JSONParser, FormParser ]


    def get_object(self):
        obj = super().get_object()
        if obj.user != self.request.user:
            raise PermissionDenied("You do not have permission to access this business.")
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "success": True,
            "message": "Update successful!",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


