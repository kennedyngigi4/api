from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Kenautos Hub"
admin.site.site_title = "Kenautos Hub"

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/account/", include("apps.accounts.urls")),
    path("api/account/dealers/", include("apps.accounts.dealers.urls")),
    path("api/dealers/", include("apps.listings.dealers.urls")),
    path("api/listings/", include("apps.listings.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/marketing/", include("apps.marketing.urls")),
]


urlpatterns += static( settings.STATIC_URL, document_root=settings.STATIC_ROOT )
urlpatterns += static( settings.MEDIA_URL, document_root=settings.MEDIA_ROOT )
