# Generated by Django 5.1.7 on 2025-06-14 08:11

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_payment_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='account_reference',
            field=models.CharField(max_length=255, null=True, verbose_name='account reference or package ID'),
        ),
        migrations.AddField(
            model_name='payment',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='paid_by',
            field=models.UUIDField(null=True, verbose_name='owner (user)'),
        ),
        migrations.AddField(
            model_name='payment',
            name='transaction_date',
            field=models.CharField(max_length=60, null=True, verbose_name='date transacted'),
        ),
    ]
