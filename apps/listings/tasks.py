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




