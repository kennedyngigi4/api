from django.contrib import admin
from apps.payments.models import *
# Register your models here.


admin.site.register(PaymentRequest)
admin.site.register(Payment)
