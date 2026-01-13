from django.utils.timezone import now
from django.utils.timesince import timesince
from rest_framework import serializers

from apps.listings.models import Listing, ListingImage, VehicleMake, VehicleModel
from apps.listings.serializers.serializers import AuctionWithTopBidSerializer


class DealerVehicleListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    vehicle_make = serializers.CharField(source="vehicle_make.name", read_only=True)

    vehicle_model = serializers.CharField(source="vehicle_model.name", read_only=True)
    auction = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "slug", "vehicle_make",  "vehicle_model", "year_of_make", "fuel", 
            "transmission", "engine_capacity", "price", "thumbnail", "display_type", "auction", "clicks"
        ]


    def get_thumbnail(self, obj):
        request = self.context.get("request")
        first_image  = obj.images.first()

        if not first_image or not first_image.thumbnail:
            return None
        
        if request:
            return  request.build_absolute_uri(first_image.thumbnail.url)

        return first_image.thumbnail.url
    

    def get_auction(self, obj):
        if obj.display_type != "auction":
            return None

        auction = (
            obj.auctions
            .filter(status__in=["upcoming", "live"])
            .first()
        )

        if not auction:
            return None

        return AuctionWithTopBidSerializer(auction).data




class DealerVehicleDetailsSerializer(serializers.ModelSerializer):

    vehicle_make = serializers.PrimaryKeyRelatedField(
        queryset=VehicleMake.objects.all(),
    )
    vehicle_model = serializers.PrimaryKeyRelatedField(
        queryset=VehicleModel.objects.all(),
    )
    vehicle_make_name = serializers.CharField(source="vehicle_make.name", read_only=True)
    vehicle_model_name = serializers.CharField(source="vehicle_model.name", read_only=True)

    images = serializers.SerializerMethodField()
    auction = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "slug", "vehicle_make", "vehicle_make_name", "vehicle_model", "vehicle_model_name", "year_of_make", "fuel", 
            "transmission", "engine_capacity", "price", "display_type",

            "images", "mileage", "drive", "usage", "tradein", "financing", "description", "vehicle_type", "status",
            "registration_number", "availability", "clicks", "location", "auction"
        ]

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(img.image.url)
            for img in obj.images.all()
        ]

    def get_auction(self, obj):
        if obj.display_type != "auction":
            return None

        auction = (
            obj.auctions
            .filter(status__in=["upcoming", "live"])
            .first()
        )

        if not auction:
            return None

        return AuctionWithTopBidSerializer(auction).data



