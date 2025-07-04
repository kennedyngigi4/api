from django.dispatch import receiver
from django.db.models.signals import post_save
from apps.accounts.models import User, UserBusiness, Subscription



@receiver(post_save, sender=User)
def UserBusinessSignal(sender, created, instance=None, *args, **kwargs):
    if created:
        business = UserBusiness.objects.create(
            user=instance,
            name=instance.name,
            email=instance.email,
            phone=instance.phone,
        )
        business.save()


