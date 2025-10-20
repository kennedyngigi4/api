from celery import Celery, shared_task
from django.utils import timezone
from apps.listings.models import *
from datetime import timedelta




@shared_task
def deactivate_expired_listings():
    now = timezone.now()
    expired_listings = Listing.objects.filter(expires_at__lte=now, status="published")
    for listing in expired_listings:
        listing.status = "expired"
        listing.save()



@shared_task
def update_auction_status():
    now = timezone.now()

    # set to live
    live_auctions =  Auction.objects.filter(
        status="upcoming",
        start_time__lte=now,
        end_time__gt=now
    )
    live_auctions.update(status="live")

    for auction in live_auctions.select_related("vehicle"):
        if auction.vehicle:
            auction.vehicle.display_type = "auction"
            auction.vehicle.save(update_fields=["display_type"])


    # Set to ended
    ended_auctions = Auction.objects.filter(
        status="live",
        end_time__lte=now
    )
    ended_auctions.update(status="ended")

    for auction in ended_auctions.select_related("vehicle"):
        if auction.vehicle:
            auction.vehicle.display_type = ""
            auction.vehicle.save(update_fields=["display_type"])
