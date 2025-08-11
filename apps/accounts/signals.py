
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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




@receiver(post_save, sender=User)
def send_welcome_email(sender, created, instance, **kwargs):
    if created:
        subject = "Welcome to Kenautos Hub"
        from_email = None
        to = [instance.email]

        html_content = render_to_string("accounts/welcome_email.html", { "user": instance })
        text_content = "Welcome to Kenautos! We’re excited to have you on board."

        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()


