from django.db.models import F, Prefetch
from django.core.cache import cache

from apps.accounts.models import User, UserBusiness
from apps.listings.models import Listing, ListingImage


class ListingService:

    @staticmethod
    def get_listing_user_ids():
        cache_key = "active_listing_seller_ids"
        user_ids = cache.get(cache_key)

        if not user_ids:
            user_ids = list(
                Listing.objects.using("listings").filter(
                    availability="Available", status="published"
                ).values_list(
                    "sold_by", flat=True
                ).distinct()
            )

            cache.set(cache_key, user_ids, 60)

        return user_ids
    

    @staticmethod
    def user_data_by_ids(user_ids):

        if not user_ids:
            return User.objects.none()


        return (
            User.objects.using("accounts").select_related(
                "business"
            ).filter(
                uid__in=user_ids
            ).only(
                "uid", 
                "is_verified",
                "date_joined",
                
                "business__id", 
                "business__name",
                "business__email", 
                "business__phone", 
                "business__image", 
                "business__banner",
            )
        )


    @staticmethod
    def get_active_auction(listing):
        return (
            listing.auctions
            .filter(status__in=["upcoming", "live"])
            .order_by("start_time")
            .first()
        )

