# Generated by Django 4.2.7 on 2023-11-18 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0023_product_total_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='five',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='four',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='one',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='three',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='feedback',
            name='two',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
