from django.urls import path
from apps.management.views import *


urlpatterns = [
    path( "dashboard/", AdminDashboardView.as_view(), name="dashboard", ),
    path( "listings/", AdminListingsView.as_view(), name="listings", ),
    path( "blog-categories/", BlogCategoriesView.as_view(), name="blog-categories", ),
    path( "blogs/", AdminBlogsView.as_view(), name="blogs", ),
    path( "hire-bookings/", AdminHireBookings.as_view(), name="hire-booking", ),
    path( "search-requests/", AdminCarSearchRequests.as_view(), name="search-requests", ),
    path( "vehicle-update/<str:pk>/", AdminVehicleUpdateView.as_view(), name="vehicle-update", ),
    path( "create-auction/", CreateAuctionView.as_view(), name="create-auction", ),
]

