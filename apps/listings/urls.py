from django.urls import path
from apps.listings.views.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"all", AllListingsViewSet, basename="all"),
router.register(r"auctions", AuctionListingsViewSet, basename="auctions"),
router.register(r"spares", SparePartsView, basename="spares"),
urlpatterns = router.urls

urlpatterns += [
    path( "makes/<str:vehicle_type>", VehicleMakesView.as_view(), name="makes", ),
    path( "models/<str:make>", VehicleModelsView.as_view(), name="models"),
    path( "home_view/", HomepageView.as_view(), name="home_view", ),
    path( "dealer_profile/<str:uid>", DealerProfileVehiclesView.as_view(), name="dealer_profile", ),
    path( "search_request", searchRequestView.as_view(), name="search_request", ),
    path( "car_hire", CarHireBookingView.as_view(), name="car_hire", ),
    path( "spares_types/", PartTypesView.as_view(), name="spares_types", ),
    path( "place-bid/", SubmitBidView.as_view(), name="place-bid", ),
    
]