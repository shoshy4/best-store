# Generated by Django 4.2.7 on 2023-12-07 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0041_alter_order_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='default',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
