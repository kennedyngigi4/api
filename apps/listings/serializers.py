from django.db import connections
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework import serializers
from apps.listings.models import *
from dateutil.relativedelta import relativedelta
from apps.accounts.serializers import *

User = get_user_model()


class VehicleMakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleMake
        fields = [
            "id","name"
        ]



class VehicleModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleModel
        fields = [
            "id", "name", "vehicle_make"
        ]


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = [
            "image_id", "image", "listing"
        ]



class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = [
            "id", "listing", "price", "updated_at"
        ]



class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, required=False)
    make = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    dealer = serializers.SerializerMethodField()
    price_drop = serializers.SerializerMethodField()
    price_dropped = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "vehicle_type", "vehicle_make", "make", "vehicle_model", "model", "year_of_make", "fuel", "mileage", "drive", 
            "transmission", "engine_capacity", "price", "usage", "tradein", "financing", "description", "vehicle_type", "status", "slug",
            "registration_number", "images", "availability", "dealer", "created_at", "updated_at", "expires_at", "price_drop", "price_dropped"
        ]


    def get_make(self, obj):
        return obj.vehicle_make.name

    def get_model(self, obj):
        return obj.vehicle_model.name


    def get_dealer(self, obj):
        try:
            user =  User.objects.using("accounts").get(uid=obj.sold_by)
            duration = self.get_joined_duration(user.date_joined)
            if user.image:
                image_url = user.image.url
            else:
                image_url = user.name[0].upper() if user.name else None

            return {
                "id": user.uid,
                "name": user.business.name,
                "phone": user.business.phone,
                "joined_since": duration,
                "image": image_url,
                "banner": user.business.banner.url if user.business.banner else None,
            }

        except User.DoesNotExist:
            return None
        
    def get_joined_duration(self, date_joined):
        now = timezone.now()
        diff = relativedelta(now, date_joined)

        if diff.years >= 1:
            return f"Joined {diff.years} years{'s' if diff.years > 1 else ''} ago"
        elif diff.months >= 1:
            return f"Joined {diff.months} month{'s' if diff.months > 1 else ''} ago"
        elif diff.weeks >= 1:
            return f"Joined {diff.weeks} week{'s' if diff.weeks > 1 else ''} ago"
        elif diff.days >= 1:
            return f"Joined {diff.days} day{'s' if diff.days > 1 else ''} ago"
        else:
            return f"Joined today"



    def get_price_drop(self, obj):
        return obj.get_price_drop()


    def get_price_dropped(self, obj):
        return obj.has_price_dropped()




class DealerWithVehiclesSerializer(serializers.Serializer):
    user = ProfileSerializer()
    vehicles = ListingSerializer(many=True)





class searchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = searchRequest
        fields = [
            "name", "phone", "make", "model", "budget", "notes"
        ]



class CarHireBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarHireBooking
        fields = [
            "fullname", "phone", "occasion", "vehicle", "occasion_date", "pickup_time", "pickup_location", "additionals"
        ]


class PartTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartType
        fields = [
            "id","name"
        ]


class PartImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartImage
        fields = [
            "id", "image", "spare_part"
        ]


class SparePartSerializer(serializers.ModelSerializer):
    images = PartImageSerializer(many=True, required=False)
    make = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    dealer = serializers.SerializerMethodField()
    spare_name = serializers.SerializerMethodField()

    class Meta:
        model = SparePart
        fields = [
            "id", "vehicle_type", "title", "vehicle_make", "vehicle_model", "parts_type", "spare_name", "condition", "price", 
            "description", "images", "make", "model", "dealer", "status", "expires_at", "slug"
        ]


    def get_make(self, obj):
        return obj.vehicle_make.name

    def get_model(self, obj):
        return obj.vehicle_model.name


    def get_spare_name(self, obj):
        return obj.parts_type.name


    def get_dealer(self, obj):
        try:
            user =  User.objects.using("accounts").get(uid=obj.sold_by)
            duration = self.get_joined_duration(user.date_joined)
            if user.image:
                image_url = user.image.url
            else:
                image_url = user.name[0].upper() if user.name else None

            return {
                "id": user.uid,
                "name": user.name,
                "phone": user.phone,
                "joined_since": duration,
                "image": image_url,
            }

        except User.DoesNotExist:
            return None
        
    def get_joined_duration(self, date_joined):
        now = timezone.now()
        diff = relativedelta(now, date_joined)

        if diff.years >= 1:
            return f"Joined {diff.years} years{'s' if diff.years > 1 else ''} ago"
        elif diff.months >= 1:
            return f"Joined {diff.months} month{'s' if diff.months > 1 else ''} ago"
        elif diff.weeks >= 1:
            return f"Joined {diff.weeks} week{'s' if diff.weeks > 1 else ''} ago"
        elif diff.days >= 1:
            return f"Joined {diff.days} day{'s' if diff.days > 1 else ''} ago"
        else:
            return f"Joined today"

