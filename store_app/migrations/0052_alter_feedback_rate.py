# Generated by Django 4.2.7 on 2023-12-13 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0051_alter_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='rate',
            field=models.IntegerField(choices=[(5, 'excellent'), (4, 'very good'), (3, 'good'), (2, 'not bad'), (1, 'bad')], null=True),
        ),
    ]
