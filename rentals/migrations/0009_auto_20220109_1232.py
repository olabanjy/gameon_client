# Generated by Django 3.2.9 on 2022-01-09 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rentals', '0008_auto_20220108_2312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rentalqueitems',
            name='from_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='rentalqueitems',
            name='to_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
