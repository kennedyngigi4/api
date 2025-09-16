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
    Auction.objects.filter(
        status="upcoming",
        start_time__lte=now,
        end_time__gt=now
    ).update(status="live")

    # Set to ended
    Auction.objects.filter(
        status="live",
        end_time__lte=now
    ).update(status="ended")
