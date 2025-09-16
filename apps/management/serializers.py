from django.utils import timezone

from rest_framework import serializers
from apps.accounts.models import *
from apps.listings.models import *
from apps.marketing.models import *
from dateutil.relativedelta import relativedelta



class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = "__all__"


class ListingsWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            "listing_id", "vehicle_type", "vehicle_make", "vehicle_model", "year_of_make", "fuel", "mileage", "drive", 
            "transmission", "engine_capacity", "price", "usage", "tradein", "financing", "description", "vehicle_type", "status",
            "availability", "updated_at", "expires_at", "clicks", "display_type"
        ]



class ListingsReadSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, required=False, read_only=True)
    make = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    dealer = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "vehicle_type", "vehicle_make", "make", "vehicle_model", "model", "year_of_make", "fuel", "mileage", "drive", 
            "transmission", "engine_capacity", "price", "usage", "tradein", "financing", "description", "vehicle_type", "status", "slug",
            "registration_number", "images", "availability", "dealer", "created_at", "updated_at", "expires_at", "clicks", "location", "display_type"
        ]

    def get_make(self, obj):
        return obj.vehicle_make.name
    
    def get_model(self, obj):
        return obj.vehicle_model.name
    

    def get_dealer(self, obj):
        try:
            user = User.objects.using("accounts").get(uid=obj.sold_by)
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
                "is_verified": user.is_verified,
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



class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = [
            "id","name"
        ]
        read_only_fields = ["id"]


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id", "title", "slug", "exerpt", "content", "image", "category", "uploaded_at", "uploaded_by"
        ]
        read_only_fields = [ "id", "slug", "uploaded_at", "uploaded_by" ] 



class CarHireSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarHireBooking
        fields = [
            "id", "fullname", "phone", "occasion", "vehicle", "occasion_date", "pickup_time", 
            "pickup_location","additionals", "status", "created_at"
        ]
        read_only_fields = [ "id", "created_at" ]



class CarSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = searchRequest
        fields = [
            "id", "name", "phone", "make", "model", "budget", "notes", "status", "created_at"
        ]
        read_only_fields = [ "id", "created_at"]




class AuctionWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = [
            "vehicle", "starting_price", "reserve_price", "buy_now_price", "start_time", "end_time", "status"
        ]
        read_only_fields = ["id", "updated_at"]

