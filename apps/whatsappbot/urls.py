from django.urls import path
from apps.whatsappbot.views import whatsapp_webhook



urlpatterns = [
    path( "webhook/", whatsapp_webhook, name="webhook", ),
]


