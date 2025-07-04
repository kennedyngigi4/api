import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class PaymentRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, verbose_name=_("unique ID"))
    owner = models.UUIDField(verbose_name=_("owner (user)"))
    package = models.UUIDField(verbose_name=_("package (selected package)"))
    checkout_request_id = models.CharField(max_length=100, unique=True)
    merchant_request_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[("PENDING", "Pending"), ("PAID", "Paid"), ("FAILED", "Failed")], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    vehicle = models.UUIDField(null=True, blank=True, verbose_name=_("vehicle (unit published first)"))

    def __str__(self):
        return str(self.checkout_request_id)
    




class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True, verbose_name=_("unique ID"))
    transaction_id = models.CharField(max_length=50, null=True, verbose_name=_("payment ID"))
    amount = models.DecimalField(max_digits=10, null=True, decimal_places=4, verbose_name=_("amount"))
    phone = models.CharField(max_length=15, null=True, verbose_name=_("phone number"))
    transaction_date = models.CharField(max_length=60, null=True, verbose_name=_("date transacted"))
    created_at = models.DateTimeField(auto_now_add=True)
    subscription = models.UUIDField(null=True, verbose_name=_("subscription (subscription)"))
    paid_by = models.UUIDField(null=True, verbose_name=_("owner (user)"))

    def __str__(self):
        return str(self.id)

