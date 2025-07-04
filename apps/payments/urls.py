from django.urls import path
from apps.payments.views import *

urlpatterns = [
    path( "purchase_subscription/", SubscriptionPurchase.as_view(), name="purchase_subscription", ),
    path( "mpesa_callback/", PaymentView.as_view(), name="mpesa_callback", ),
]

