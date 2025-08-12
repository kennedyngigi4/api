import django_filters
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.listings.models import *
from apps.listings.serializers import *


# Cache for 1 week in seconds
CACHE_TIMEOUT = 60 * 60 * 24 * 7

class VehicleMakesView(generics.ListAPIView):
    serializer_class = VehicleMakeSerializer
    queryset = VehicleMake.objects.all().order_by("name")

    def get_queryset(self):
        vehicle_type = "car" if self.kwargs["vehicle_type"] == "truck" else self.kwargs["vehicle_type"]
        cache_key = f"vehicle_makes_{vehicle_type}"

        data = cache.get(cache_key)
        if data is None:
            data = list(self.queryset.filter(vehicle_type=vehicle_type))
            cache.set(cache_key, data, timeout=CACHE_TIMEOUT)
        return data



class VehicleModelsView(generics.ListAPIView):
    serializer_class = VehicleModelSerializer
    queryset = VehicleModel.objects.all().order_by("name")

    def get_queryset(self):
        filtered_make = self.kwargs["make"]
        cache_key = f"vehicle_models_{filtered_make}"

        data = cache.get(cache_key)
        if data is None:
            data = list(VehicleModel.objects.filter(vehicle_make=filtered_make).order_by("name"))
            cache.set(cache_key, data, timeout=CACHE_TIMEOUT)
        return data
    


class HomepageView(APIView):
    def get(self, request):
        top_luxury = Listing.objects.filter(
            is_top=True, status="published", availability="Available"
        ).order_by("-updated_at")

        latest_cars = Listing.objects.filter(
            is_top=False, status="published", availability="Available", vehicle_type="car"
        ).order_by("-updated_at")[:12]

        latest_bikes = Listing.objects.filter(
            is_top=False, status="published", availability="Available", vehicle_type="bike"
        ).order_by("-updated_at")[:4]

        latest_trucks = Listing.objects.filter(
            is_top=False, status="published", availability="Available", vehicle_type="truck"
        ).order_by("-updated_at")[:4]

        data = {
            "luxuries": ListingSerializer(top_luxury, many=True).data,
            "cars": ListingSerializer(latest_cars, many=True).data,
            "bikes": ListingSerializer(latest_bikes, many=True).data,
            "trucks": ListingSerializer(latest_trucks, many=True).data,
        }

        return Response(data)


class ListingFilter(django_filters.FilterSet):
    # Filter
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    make = django_filters.CharFilter(field_name="vehicle_make__name", lookup_expr="icontains")
    model = django_filters.CharFilter(field_name="vehicle_model__name", lookup_expr="icontains")
    yom = django_filters.CharFilter(field_name="year_of_make", lookup_expr="exact")
    usage = django_filters.CharFilter(field_name="usage", lookup_expr="iexact")

    class Meta:
        model = Listing
        fields = [ 'make', 'model', 'year_of_make', 'min_price', 'max_price', 'vehicle_type' ]


class SparesFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains" )
    make = django_filters.CharFilter(field_name="vehicle_make__name", lookup_expr="icontains" )
    model = django_filters.CharFilter(field_name="vehicle_model__name", lookup_expr="icontains" )
    parts_type = django_filters.CharFilter(field_name="parts_type__name", lookup_expr="icontains" )
    vehicle_type = django_filters.CharFilter(field_name="vehicle_type", lookup_expr="icontains" )

    class Meta:
        model = SparePart
        fields = [ 'title', 'make', 'model', 'parts_type', 'vehicle_type', 'min_price', 'max_price' ]


class ListingPagination(PageNumberPagination):
    page_size = 23
    page_size_query_param = "page_size"
    max_page_size = 100



@method_decorator(cache_page(60), name="dispatch")
class AllListings(ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    pagination_class = ListingPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter
    lookup_field = "slug"

    def get_queryset(self):
        queryset = self.queryset.filter(availability="Available", status="published")
        vehicle_type = self.request.query_params.get('vehicle_type')
        if vehicle_type:
            queryset = queryset.filter(vehicle_type=vehicle_type)
        return  queryset.order_by("-updated_at")


@method_decorator(cache_page(60), name="dispatch")
class SparePartsView(ModelViewSet):
    queryset = SparePart.objects.all().order_by("-created_at")
    serializer_class = SparePartSerializer
    pagination_class = ListingPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = SparesFilter

    def get_queryset(self):
        queryset = self.queryset.filter(status="published")
        return queryset.order_by("-updated_at")


class ListingDetailsView(generics.RetrieveAPIView):
    serializer_class = ListingSerializer
    queryset = Listing.objects.filter(availability="Available", status="published")
    lookup_field = "slug"



class DealerProfileVehiclesView(APIView):
    def get(self, request, uid):
        try:
            user = User.objects.get(uid=uid)
        except User.DoesNotExist:
            return Response({ "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Vehicles posted by the dealer
        vehicles = Listing.objects.using("listings").filter(sold_by=uid, availability="Available", status="published")

        data = {
            "user": user,
            "vehicles": vehicles
        }

        serializer = DealerWithVehiclesSerializer(data)
        return Response(serializer.data)




class searchRequestView(generics.CreateAPIView):
    serializer_class = searchRequestSerializer
    queryset = searchRequest.objects.all()

    def post(self, request):
        serializer = searchRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True }, status=status.HTTP_200_OK)
        return Response({ "success": False, "error": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)


class CarHireBookingView(generics.CreateAPIView):
    serializer_class = CarHireBookingSerializer
    queryset = CarHireBooking.objects.all()

    def post(self, request):
        serializer = CarHireBookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({ "success": True }, status=status.HTTP_200_OK)
        return Response({ "success": False, "error": "Something went wrong."}, status=status.HTTP_400_BAD_REQUEST)




class PartTypesView(generics.ListAPIView):
    serializer_class = PartTypeSerializer
    queryset = PartType.objects.all().order_by("name")





