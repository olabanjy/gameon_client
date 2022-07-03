# Generated by Django 3.2.9 on 2022-06-17 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0008_order_delivery_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='instant_delivery_eligible',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='instant_delivery_vendor',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='vendor_code',
            field=models.CharField(default='admin', max_length=200),
        ),
        migrations.AlterField(
            model_name='order',
            name='delivery_option',
            field=models.CharField(default='standard', max_length=200),
        ),
    ]
