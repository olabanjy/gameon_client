# Generated by Django 3.2.9 on 2022-02-12 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0011_rentalgametrailer_trailer_yt_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='rentalque',
            name='shipping_fee',
            field=models.IntegerField(default=0),
        ),
    ]
