# Generated by Django 5.1.7 on 2025-05-26 04:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_alter_userbusiness_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SubscriptionPackage',
            new_name='Package',
        ),
        migrations.RenameModel(
            old_name='UserSubscription',
            new_name='Subscription',
        ),
    ]
