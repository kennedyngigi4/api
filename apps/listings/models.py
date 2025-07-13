import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from datetime import timedelta

# Create your models here.

class FreePostingMode(models.Model):
    is_active = models.BooleanField(default=False)
    free_duration_days = models.IntegerField(default=7)
    post_duration = models.IntegerField(default=14)
    activated_at = models.DateTimeField(null=True, blank=True)

    def is_currently_active(self):
        return self.is_active and self.activated_at and (
            timezone.now() < self.activated_at + timedelta(days=self.free_duration_days)
        )
    
    def __str__(self):
        return "Free Posting Mode"


class VehicleMake(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ( "car", "Car", ),
        ( "bike", "Bike", ),
    ]


    name = models.CharField(max_length=255, null=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES, null=True)

    def __str__(self):
        return self.name


class VehicleModel(models.Model):
    name = models.CharField(max_length=255, null=True)
    vehicle_make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name
    

class Listing(models.Model):

    availability_list = (
        ( "Available", "Available", ),
        ( "Sold", "Sold", ),
        ( "Reserved", "Reserved", ),
    )

    VEHICLE_TYPE_CHOICES = [
        ( "car", "Car", ),
        ( "bike", "Bike", ),
        ( "truck", "Truck", ),
    ]


    STATUS_CHOICES = [
        ( "draft", "Draft", ),
        ( "pending_review", "Pending Review", ),
        ( "published", "Published", ),
        ( "expired", "Expired", ),
    ]

    listing_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    vehicle_type = models.CharField(max_length=30, null=True, choices=VEHICLE_TYPE_CHOICES, blank=True)
    vehicle_make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE, null=True)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, null=True)
    year_of_make = models.CharField(max_length=20, null=True, blank=True)
    fuel = models.CharField(max_length=40, null=True, blank=True)
    mileage = models.CharField(max_length=60, null=True, blank=True)
    drive = models.CharField(max_length=20, null=True, blank=True)
    transmission = models.CharField(max_length=30, null=True, blank=True)
    engine_capacity = models.CharField(max_length=30, null=True, blank=True)
    price = models.CharField(max_length=60, null=True, blank=True)
    usage = models.CharField(max_length=20, null=True, blank=True)
    tradein = models.BooleanField(default=False)
    financing = models.BooleanField(default=False)
    description = models.TextField(null=True, blank=True)
    availability = models.CharField(max_length=50, choices=availability_list, default=availability_list[0][0], null=True, blank=True) #todo sold, available, reserved, 
    registration_number = models.CharField(max_length=6, null=True, blank=True)
    is_top = models.BooleanField(default=False)

    sold_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    package_type = models.CharField(max_length=50, null=True, blank=True)
    was_free_post = models.BooleanField(default=False)
    status = models.CharField(max_length=60, choices=STATUS_CHOICES, default="draft")
    slug = models.SlugField(unique=True, blank=True)


    def get_price_drop(self):
        last_record = self.price_history.order_by("-updated_at").first()
        return last_record.price if last_record else None
    
    def has_price_dropped(self):
        price_drop = self.get_price_drop()
        if price_drop is not None:
            return price_drop < self.price
        return False
    

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.year_of_make}-{self.vehicle_make.name}-{self.vehicle_model.name}")
            unique_suffix = uuid.uuid4().hex[:20]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.year_of_make} {self.vehicle_make} {self.vehicle_model}"


def ListingImagePath(instance, filename):
    user_id = str(instance.listing.sold_by).replace("-","")
    listing_id = str(instance.listing.listing_id).replace("-","")
    return f"vehicles/{user_id}/{listing_id}/{filename}"


class ListingImage(models.Model):
    image_id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    image = models.ImageField(upload_to=ListingImagePath, blank=True, null=True)
    listing = models.ForeignKey(Listing, related_name="images", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.listing.listing_id}"
    


class PriceHistory(models.Model):
    listing = models.ForeignKey(Listing,  related_name="price_history", on_delete=models.CASCADE, null=True)
    price = models.CharField(max_length=60, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.listing.year_of_make} {self.listing.vehicle_make} {self.listing.vehicle_model}"



class PartType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class SparePart(models.Model):

    VEHICLE_TYPE_CHOICES = [
        ( "car", "Car", ),
        ( "bike", "Bike", ),
        ( "truck", "Truck", ),
    ]

    CONDITION_TYPES = [
        ( "brand new", "Brand New", ),
        ( "used", "Used", ),
        ( "refurbished", "Refurbished", ),
    ]

    STATUS_CHOICES = [
        ( "draft", "Draft", ),
        ( "pending_review", "Pending Review", ),
        ( "published", "Published", ),
        ( "expired", "Expired", ),
    ]

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    title = models.TextField()
    vehicle_type = models.CharField(max_length=255, null=True, choices=VEHICLE_TYPE_CHOICES, blank=True)
    vehicle_make = models.ForeignKey(VehicleMake, on_delete=models.CASCADE, null=True)
    vehicle_model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, null=True)
    parts_type = models.ForeignKey(PartType, on_delete=models.CASCADE)
    condition = models.CharField(max_length=255, choices=CONDITION_TYPES)
    price = models.IntegerField()
    description = models.TextField()
    sold_by = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True)
    expires_at = models.DateTimeField(auto_now=True, null=True)
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default="draft")
    free_post = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.vehicle_make.name}-{self.vehicle_model.name}")
            unique_suffix = uuid.uuid4().hex[:20]
            self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)



    def __str__(self):
        return self.title


def PartImagePath(instance, filename):
    user_id = str(instance.spare_part.sold_by).replace("-","")
    partid = str(instance.spare_part.id).replace("-","")
    return f"parts/{user_id}/{partid}/{filename}"


class PartImage(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    image = models.ImageField(upload_to=PartImagePath, blank=True, null=True)
    spare_part = models.ForeignKey(SparePart, related_name="images", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.spare_part.id}"




class searchRequest(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    name = models.CharField(max_length=70, verbose_name=_("client name"))
    phone = models.CharField(max_length=15, verbose_name=_("client phone number"))
    make  = models.CharField(max_length=60, verbose_name=_("preferred make"))
    model = models.CharField(max_length=60, verbose_name=_("preferred model"))
    budget = models.CharField(max_length=60, verbose_name=_("budget"))
    notes = models.TextField(null=True, blank=True, verbose_name=_("extra specifications"))
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.name} - {self.make} {self.model}"


class CarHireBooking(models.Model):
    id  = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, unique=True)
    fullname = models.CharField(max_length=70, verbose_name=_("client name"))
    phone = models.CharField(max_length=15, verbose_name=_("client phone number"))
    occasion = models.CharField(max_length=50, verbose_name=_("occasion type"))
    vehicle  = models.CharField(max_length=60, verbose_name=_("preferred vehicle"))
    occasion_date = models.CharField(max_length=15, verbose_name=_("occasion date"))
    pickup_time = models.CharField(max_length=15, verbose_name=_("pickup time"))
    pickup_location = models.CharField(max_length=255, verbose_name=_("pickup location"))
    additionals = models.TextField(null=True, blank=True, verbose_name=_("extra specifications"))
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.fullname} - {self.occasion}"
