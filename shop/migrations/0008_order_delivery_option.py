# Generated by Django 3.2.9 on 2022-06-13 06:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_order_shipping_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(default='instant', max_length=200),
        ),
    ]
