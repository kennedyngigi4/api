from django.urls import path
from apps.accounts.dealers.views import BusinessUpdateView


urlpatterns = [
    path( "business_update/<str:pk>", BusinessUpdateView.as_view(), name="business_update", ),
]

