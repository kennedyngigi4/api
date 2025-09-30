from django.shortcuts import render
from django.db.models import Q

from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.models import *
from apps.listings.models import *
from apps.accounts.permissions import *

from apps.management.serializers import *
# Create your views here.


class AdminDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, *args, **kwargs):
        print("response ........")
        users = User.objects.all().exclude(is_staff=True).count()
        listings = Listing.objects.all().count()
        bookings = CarHireBooking.objects.all().count()
        requests = searchRequest.objects.all().count()


        response = {
            "users": users,
            "listings": listings,
            "bookings": bookings,
            "requests": requests
        }

        

        return Response(response)
    


class AdminListingsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def get(self, request, *args, **kwargs):
        listing_type = request.query_params.get("type", "all")
        queryset = Listing.objects.order_by("-created_at")

        if listing_type == "luxury":
            queryset = queryset.filter(display_type="luxury")
        elif listing_type == "auction":
            queryset = queryset.filter(display_type="auction")
        else:
            queryset = queryset.exclude(display_type__in=["luxury", "auction"])


        serializer = ListingsReadSerializer(queryset, many=True)
        return Response(serializer.data)


class BlogCategoriesView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def get(self, request, *args, **kwargs):
        queryset = BlogCategory.objects.all().order_by("name")
        serializer = BlogCategorySerializer(queryset, many=True)

        return Response(serializer.data)
    


class AdminBlogsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def post(self, request):
        serializer = BlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(uploaded_by=self.request.user.uid)

        return Response({"success": True, "message": "Blog created!"}, status=status.HTTP_201_CREATED)
    
    def get(self, request, *args, **kwargs):
        queryset = Blog.objects.filter(uploaded_by=self.request.user.uid).order_by("-uploaded_at")
        serializer = BlogSerializer(queryset, many=True)

        return Response(serializer.data)



class AdminHireBookings(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def get(self, request):
        queryset = CarHireBooking.objects.all().order_by("-created_at")
        serializer = CarHireSerializer(queryset, many=True)

        return Response(serializer.data)
    

class AdminCarSearchRequests(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def get(self, request):
        queryset = searchRequest.objects.all().order_by("-created_at")
        serializer = CarSearchSerializer(queryset, many=True)

        return Response(serializer.data)



class AdminVehicleUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]
    serializer_class = ListingsWriteSerializer
    queryset = Listing.objects.all()

    def update(self, request, *args, **kwargs):
        partial = True
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "success": True,
            "message": "Vehicle updated successfully",
        }, status=status.HTTP_200_OK)




class CreateAuctionView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]
    
    def post(self, request, *args, **kwargs):
        serializer = AuctionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(updated_by=self.request.user.uid)

        return Response({
            "success": True,
            "message": "Auction set.",
        }, status=status.HTTP_201_CREATED)





class BidsViews(APIView):
    permission_classes = [IsAuthenticated, IsAdmin, IsManager]

    def get(self, request, *args, **kwargs):
        queryset = Bid.objects.all()
        serializer = BidsSerializer(queryset, many=True)
        return Response(serializer.data)
