# Generated by Django 4.2.7 on 2023-12-11 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0045_remove_cart_total_price_remove_cartitem_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='total_price',
        ),
        migrations.AlterField(
            model_name='order',
            name='order_status',
            field=models.IntegerField(choices=[(1, 'Completed. Payment in process'), (2, 'Not completed yet. Make sure payment_details and shipping_address are added'), (3, 'Paid. In process'), (4, "Sent to customer's shipping address"), (5, 'Delivered'), (6, 'Received')], default=1),
        ),
    ]