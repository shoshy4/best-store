# Generated by Django 4.2.7 on 2023-11-12 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='amount',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.FloatField(),
        ),
    ]
