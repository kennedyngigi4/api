from django.contrib import admin
from apps.accounts.models import User, UserBusiness, Package, Subscription
# Register your models here.

admin.site.register(User)
admin.site.register(UserBusiness)
admin.site.register(Package)
admin.site.register(Subscription)
