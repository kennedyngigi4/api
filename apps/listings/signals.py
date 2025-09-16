from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.listings.models import *



@receiver(post_save, sender=Auction)
def update_listing_to_auction(sender, instance, created, **kwargs):
    if created:
        listing = instance.vehicle
        listing.display_type = "auction"
        listing.save(update_fields=["display_type"])
       


