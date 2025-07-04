from django.urls import path
from apps.marketing.views import *


urlpatterns = [
    path( "dealer_notifications", UserNotificationsView.as_view(), name="dealer_notifications", ),
]


