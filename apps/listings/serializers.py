from django.db.models import Prefetch 
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timesince import timesince
from django.utils.timezone import now


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
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = ListingImage
        fields = [
            "image_id", "image", "listing"
        ]
    


class AuctionSerializer(serializers.ModelSerializer):
    current_price = serializers.SerializerMethodField()
    highest_bid = serializers.SerializerMethodField()
    countdown_to = serializers.SerializerMethodField()

    class Meta:
        model = Auction
        fields = [
            "id", "vehicle", "starting_price", "reserve_price", "buy_now_price", "start_time", "end_time", "status",
            "current_price", "highest_bid", "countdown_to"
        ]
        read_only_fields = [ "id", "updated_at"]

    
    def get_highest_bid(self, obj):
        top_bid = obj.bids.order_by("-amount").first()
        return str(top_bid.amount) if top_bid else None


    def get_current_price(self, obj):
        top_bid = obj.bids.order_by("-amount").first()
        if top_bid:
            return str(top_bid.amount)
        return obj.starting_price
    

    def get_countdown_to(self, obj):
        now = timezone.now()
        if now < obj.start_time:
            return obj.start_time
        elif obj.start_time <= now < obj.end_time:
            return obj.end_time
        return None 


class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceHistory
        fields = [
            "id", "listing", "price", "updated_at"
        ]



class AuctionPriceSerializer(serializers.Serializer):
    starting_price = serializers.CharField()
    reserve_price = serializers.CharField(allow_null=True)
    buy_now_price = serializers.CharField(allow_null=True)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    status = serializers.CharField()


class TopBidSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    timestamp = serializers.DateTimeField()


class AuctionWithTopBidSerializer(serializers.Serializer):
    starting_price = serializers.CharField()
    reserve_price = serializers.CharField(allow_null=True)
    buy_now_price = serializers.CharField(allow_null=True)
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    status = serializers.CharField()
    top_bid = serializers.SerializerMethodField()

    def get_top_bid(self, obj):
        bid = obj.bids.select_related("bidder").first()
        if not bid:
            return None
        return TopBidSerializer(bid).data



class VehicleListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()
    vehicle_make = serializers.CharField(source="vehicle_make.name", read_only=True)
    vehicle_model = serializers.CharField(source="vehicle_model.name", read_only=True)
    auction = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "slug", "vehicle_make", "vehicle_model", "year_of_make", "fuel", 
            "transmission", "engine_capacity", "price", "thumbnail", "display_type", "auction"
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



    

class SellerBusinessSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    image = serializers.CharField(allow_null=True)
    banner = serializers.CharField(allow_null=True)


class VehicleDetailsSerializer(serializers.ModelSerializer):
    vehicle_make = serializers.CharField(source="vehicle_make.name", read_only=True)
    vehicle_model = serializers.CharField(source="vehicle_model.name", read_only=True)
    images = serializers.SerializerMethodField()
    seller = serializers.SerializerMethodField()
    auction = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "slug", "vehicle_make", "vehicle_model", "year_of_make", "fuel", 
            "transmission", "engine_capacity", "price", "display_type",

            "images", "mileage", "drive", "usage", "tradein", "financing", "description", "vehicle_type", "status",
            "registration_number", "availability", "clicks", "location", "seller", "auction"
        ]

    def get_images(self, obj):
        request = self.context.get("request")
        return [
            request.build_absolute_uri(img.image.url)
            for img in obj.images.all()
        ]


    def get_seller(self, obj):
        sellers_map = self.context.get("sellers_map", {})
        user = sellers_map.get(str(obj.sold_by))

        if not user or not hasattr(user, "business"):
            return None

        business = user.business
        request = self.context.get("request")

        return {
            "id": business.id,

            # Business info
            "name": business.name,
            "email": business.email,
            "phone": business.phone,
            "image": (
                request.build_absolute_uri(business.image.url)
                if business.image else None
            ),
            "banner": (
                request.build_absolute_uri(business.banner.url)
                if business.banner else None
            ),

            # User info
            "is_verified": user.is_verified,
            "date_joined": user.date_joined,
            "joined_since": (
                "today"
                if timesince(user.date_joined, now()) == "0 minutes"
                else f"{timesince(user.date_joined, now())} ago"
            ),
        }


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













class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, required=False, read_only=True)
    make = serializers.SerializerMethodField()
    model = serializers.SerializerMethodField()
    dealer = serializers.SerializerMethodField()
    price_drop = serializers.SerializerMethodField()
    price_dropped = serializers.SerializerMethodField()
    auctions = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "listing_id", "vehicle_type", "vehicle_make", "make", "vehicle_model", "model", "year_of_make", "fuel", "mileage", "drive", 
            "transmission", "engine_capacity", "price", "usage", "tradein", "financing", "description", "vehicle_type", "status", "slug",
            "registration_number", "images", "availability", "dealer", "created_at", "updated_at", "expires_at", "price_drop", 
            "price_dropped", "clicks", "location", "display_type", "auctions"
        ]

    def get_auctions(self, obj):
        auction = (
            obj.auctions.filter(status__in=["live", "upcoming"])
            .order_by(
                models.Case(
                    models.When(status="live", then=0),
                    models.When(status="upcoming", then=1),
                    default=2,
                    output_field=models.IntegerField(),
                ),
                "-updated_at",
            )
            .first()
        )
        return AuctionSerializer(auction).data if auction else None
                

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
    images = PartImageSerializer(many=True, required=False, read_only=True)
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





class BidSubmissionSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    auction = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)


    def create(self, validated_data):
        # Step 1: get or create bidder
        bidder, _ = Bidder.objects.get_or_create(
            phone=validated_data["phone"],
            defaults={"name": validated_data["name"]}
        )

        # Step 2: get auction
        auction = Auction.objects.get(id=validated_data["auction"])

        # Step 3: create bid
        bid = Bid.objects.create(
            auction=auction,
            bidder=bidder,
            amount=validated_data["amount"]
        )

        return bid


