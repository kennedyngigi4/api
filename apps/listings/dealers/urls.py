from django.urls import path
from apps.listings.dealers.views import *


urlpatterns = [
    path( "eligibility_check/", uploadEligibilityCheckView.as_view(), name="eligibility_check", ),
    path( "upload", VehicleUploadView.as_view(), name="upload", ),
    path( "images_upload", ListingImageUploadView.as_view(), name="images_upload", ),
    path( "vehicles/", DealerVehiclesList.as_view(), name="vehicles", ),
    path( "vehicle/<slug:slug>", VehicleDetailsView.as_view(), name="vehicle", ),
    path( "vehicle_delete/<slug:slug>", VehicleDeleteView.as_view(), name="vehicle_delete", ),
    path( "vehicle_image_delete/<str:pk>", VehicleImageDeleteView.as_view(), name="vehicle_image_delete"),
    path( "new_images", VehicleNewImagesView.as_view(), name="new_images", ),
    path( "price_history/", PriceHistoryView.as_view(), name="price_histoty", ),
    path( "spare_upload/", UploadSparePartsView.as_view(), name="spare_upload", ),
    path( "spare_images_upload/", SpareImagesUploadView.as_view(), name="spare_images_upload", ),
    path( "my_spares/", DealerSparesListView.as_view(), name="my_spares", ),
    path( "spare/<str:pk>", SparesRetrieveEditDeleteView.as_view(), name="spare", ),
    path( "packages/", PackagesView.as_view(), name="packages", ),
]



