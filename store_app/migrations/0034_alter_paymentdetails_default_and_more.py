# Generated by Django 4.2.7 on 2023-11-20 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0033_paymentdetails_default_shippingaddress_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='paymentdetails',
            name='default',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='default',
            field=models.BooleanField(default=False),
        ),
    ]