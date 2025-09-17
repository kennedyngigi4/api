from django.contrib import admin
from apps.listings.models import *
from django_celery_beat.models import PeriodicTask, IntervalSchedule

# Register your models here.


admin.site.register(VehicleMake)
admin.site.register(VehicleModel)
admin.site.register(Listing)
admin.site.register(ListingImage)
admin.site.register(FreePostingMode)
admin.site.register(searchRequest)
admin.site.register(CarHireBooking)
admin.site.register(SparePart)
admin.site.register(PartType)
admin.site.register(PartImage)
# admin.site.register(Auction)
# admin.site.register(Bid)

