# Generated by Django 5.1.7 on 2025-06-14 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_payment_phone_payment_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=4, max_digits=10, null=True, verbose_name='amount'),
        ),
    ]
