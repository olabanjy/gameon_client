from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_init, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum
from django.urls import reverse
from allauth.account.signals import user_signed_up, user_logged_in
from django_countries.fields import CountryField
from datetime import timedelta, date, datetime
from PIL import Image
import uuid
import random
import string
import pyotp
from users.models import Address, Profile
from decimal import Decimal

from geopy.distance import geodesic


class GeneralSetting(models.Model):
    location_range = models.IntegerField(blank=True, null=True)


class ItemPlatform(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=400, blank=True, null=True)
    iconImagePath = models.ImageField(
        upload_to="gameon/shop/platform/iconImagePath/",
        default="default_icon_pics.jpg",
        blank=True,
    )

    def __str__(self):
        return self.name


class ItemCat(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=400, blank=True, null=True)
    iconImagePath = models.ImageField(
        upload_to="gameon/shop/category/iconImagePath/",
        default="default_icon_pics.jpg",
        blank=True,
    )

    def __str__(self):
        return self.name


class ItemType(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=400, blank=True, null=True)
    iconImagePath = models.ImageField(
        upload_to="gameon/shop/type/iconImagePath/",
        default="default_icon_pics.jpg",
        blank=True,
    )

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=200)

    platform = models.ForeignKey(
        "ItemPlatform",
        related_name="item_platform",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    cat = models.ManyToManyField("ItemCat", related_name="item_cats", blank=True)
    type = models.ForeignKey(
        "ItemType",
        related_name="item_type",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    numberInStock = models.IntegerField(default=1)
    displayImagePath = models.ImageField(
        upload_to="gameon/shop/games/displayImagePath/",
        default="default_display_pics.jpg",
        blank=True,
    )
    bannerImagePath = models.ImageField(
        upload_to="gameon/shop/games/bannerImagePath/",
        default="default_banner_pics.jpg",
        blank=True,
    )
    thumbnailImagePath = models.ImageField(
        upload_to="gameon/shop/games/thumbnailImagePath/",
        default="default_thumbnail_pics.jpg",
        blank=True,
    )
    price = models.IntegerField()
    desc = models.TextField(blank=True, null=True)
    discount_price = models.IntegerField(blank=True, null=True)
    adminOwned = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    featured_banner = models.BooleanField(default=False)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    vendor_code = models.CharField(max_length=200, default="admin")
    vendor_long = models.FloatField(null=True, blank=True)
    vendor_lat = models.FloatField(null=True, blank=True)
    comingSoon = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("shop:details", kwargs={"item_id": self.id})

    def checkInRadius(self, destination):

        if self.vendor_lat and self.vendor_long:
            origin = (self.vendor_lat, self.vendor_long)
            print(origin, destination)

            km_dist = geodesic(origin, destination).kilometers
            print(km_dist)

            if km_dist < 50:
                return True
            else:
                return False
        else:
            return False


class OrderItem(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        # return f"{self.quantity} of {self.item.name}"
        return f"{self.pk} - {self.user} -{self.quantity}"

    def get_total_item_price(self):
        if self.item:
            return self.quantity * self.item.price
        else:
            return 0

    def get_total_discount_item_price(self):
        if self.item:
            return self.quantity * self.item.discount_price
        else:
            return 0

    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()

    def get_final_price(self):
        if self.item and self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()


class Order(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True, blank=True)
    items = models.ManyToManyField(OrderItem, related_name="order_item")
    ref_code = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(default=timezone.now)
    ordered = models.BooleanField(default=False)
    shipping_address_area = models.CharField(max_length=200, null=True)
    shipping_address = models.ForeignKey(
        Address,
        related_name="shipping_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    billing_address = models.ForeignKey(
        Address,
        related_name="billing_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    payment = models.ForeignKey(
        "Payment", on_delete=models.SET_NULL, blank=True, null=True
    )
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True
    )
    pick_up_prompt = models.BooleanField(default=False)
    shipping_fee = models.IntegerField(default=0)
    delivery_option = models.CharField(max_length=200, default="standard")
    being_delivered = models.BooleanField(default=False)
    instant_delivery_eligible = models.BooleanField(default=False)
    instant_delivery_vendor = models.CharField(max_length=200, null=True)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user}"

    def get_shipping_total(self):
        total = 0
        if self.shipping_fee == 0:
            print("adding shipping fee")
            total += self.shipping_fee
        return total

    def get_order_total(self):
        total = 0
        if self.items:
            for order_item in self.items.all():
                total += order_item.get_final_price()
        return total

    def get_total(self):
        total = 0
        if self.items:
            for order_item in self.items.all():
                total += order_item.get_final_price()
        # if self.coupon:
        #     total -= self.coupon.amount
        if self.shipping_fee:
            total += self.shipping_fee
        return total


class Payment(models.Model):
    txn_code = models.CharField(max_length=50)
    user = models.ForeignKey(Profile, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_code}"


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class WebhookBackup(models.Model):
    pay_sol = models.CharField(max_length=500, blank=True, null=True)
    the_order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True
    )
    req_body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.pay_sol


class AppLogs(models.Model):
    log_title = models.CharField(max_length=500, blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.log_title} - {self.created_at}"
