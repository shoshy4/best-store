# Generated by Django 4.2.7 on 2023-11-20 16:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0031_alter_order_created'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='created',
            new_name='created_date',
        ),
    ]