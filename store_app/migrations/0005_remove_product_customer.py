# Generated by Django 4.2.7 on 2023-11-13 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0004_alter_product_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='customer',
        ),
    ]
