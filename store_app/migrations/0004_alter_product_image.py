# Generated by Django 4.2.7 on 2023-11-12 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0003_rename_author_feedback_customer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
