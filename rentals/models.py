from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, post_init, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum
from allauth.account.signals import user_signed_up, user_logged_in
from django_countries.fields import CountryField
from datetime import timedelta, date, datetime
from PIL import Image
import uuid
import random, string
import pyotp

from django.urls import reverse
from geopy.distance import geodesic


class RentalPlatform(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=400, blank=True, null=True)
    iconImagePath = models.ImageField(
        upload_to="gameon/rental/platform/iconImagePath/",
        default="default_icon_pics.jpg",
        blank=True,
    )

    def __str__(self):
        return self.name


class RentalCat(models.Model):
    name = models.CharField(max_length=200)
    desc = models.CharField(max_length=400, blank=True, null=True)
    iconImagePath = models.ImageField(
        upload_to="gameon/rental/category/iconImagePath/",
        default="default_icon_pics.jpg",
        blank=True,
    )

    def __str__(self):
        return self.name


class RentalGame(models.Model):
    name = models.CharField(max_length=200)
    platform = models.ForeignKey(
        "RentalPlatform",
        related_name="game_platform",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    cat = models.ManyToManyField("RentalCat", related_name="game_cats")
    numberInStock = models.IntegerField(default=1)
    displayImagePath = models.ImageField(
        upload_to="gameon/rental/games/displayImagePath/",
        default="default_display_pics.jpg",
        blank=True,
    )
    bannerImagePath = models.ImageField(
        upload_to="gameon/rental/games/bannerImagePath/",
        default="default_banner_pics.jpg",
        blank=True,
    )
    thumbnailImagePath = models.ImageField(
        upload_to="gameon/rental/games/thumbnailImagePath/",
        default="default_thumbnail_pics.jpg",
        blank=True,
    )
    dailyRentalRate = models.IntegerField(default=1000)
    adminOwned = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    featured_banner = models.BooleanField(default=False)
    vendor = models.CharField(max_length=200, blank=True, null=True)
    vendor_code = models.CharField(max_length=200, blank=True, null=True)
    vendor_long = models.FloatField(null=True, blank=True)
    vendor_lat = models.FloatField(null=True, blank=True)
    comingSoon = models.BooleanField(default=False)
    desc = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("rentals:details", kwargs={"item_id": self.id})

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


class RentalGameTrailer(models.Model):
    name = models.CharField(max_length=200)
    platform = models.ForeignKey(
        "RentalPlatform",
        related_name="trailer_platform",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    trailer_banner = models.ImageField(
        upload_to="gameon/rental/trailers/bannerImagePath/",
        default="default_banner_pics.jpg",
        blank=True,
    )
    trailer_file_mp4 = models.FileField(
        upload_to="gameon/rental/trailers/mp4/",
        default="default_mp4_trailer.mp4",
        blank=True,
    )
    trailer_file_webm = models.FileField(
        upload_to="gameon/rental/trailers/mp4/",
        default="default_webm_trailer.webm",
        blank=True,
    )
    trailer_yt_link = models.CharField(max_length=400, blank=True, null=True)
    highlight_title = models.CharField(max_length=400, blank=True, null=True)
    highlight_desc = models.TextField(blank=True, null=True)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class RentalQueItems(models.Model):
    user = models.ForeignKey(
        "users.Profile", on_delete=models.SET_NULL, null=True, blank=True
    )
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(RentalGame, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    no_of_days = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.pk} - {self.user} -{self.quantity}"

    def get_total_item_price(self):
        if self.item:
            return (self.quantity * self.item.dailyRentalRate) * self.no_of_days
        else:
            return 0

    def get_final_price(self):
        return self.get_total_item_price()


class RentalQue(models.Model):
    user = models.ForeignKey(
        "users.Profile", on_delete=models.SET_NULL, null=True, blank=True
    )
    items = models.ManyToManyField(RentalQueItems, related_name="rental_que_item")
    ref_code = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(default=timezone.now)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        "users.Address",
        related_name="rental_shipping_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    shipping_address_area = models.CharField(max_length=200, null=True)
    return_prompt = models.BooleanField(default=False)
    return_address = models.ForeignKey(
        "users.Address",
        related_name="rental_return_address",
        on_delete=models.SET_NULL,
        null=True,
    )
    return_address_area = models.CharField(max_length=200, null=True)
    pick_up_prompt = models.BooleanField(default=False)
    billing_address = models.ForeignKey(
        "users.Address",
        related_name="rental_billing_address",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    payment = models.ForeignKey(
        "RentalPayment", on_delete=models.SET_NULL, blank=True, null=True
    )
    shipping_fee = models.IntegerField(default=0)
    pickup_fee = models.IntegerField(default=0)
    return_fee = models.IntegerField(default=0)
    being_delivered = models.BooleanField(default=False)
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

    def get_pickup_total(self):
        total = 0
        if self.pickup_fee == 0:
            print("adding pickup fee")
            total += self.pickup_fee

        return total

    def get_return_total(self):
        total = 0
        if self.return_fee == 0:
            print("adding return fee")
            total += self.return_fee

        return total

    def get_que_order_total(self):
        total = 0
        if self.items:
            for que_item in self.items.all():
                total += que_item.get_final_price()
        return total

    def get_total(self):
        total = 0
        if self.items:
            for que_item in self.items.all():
                total += que_item.get_final_price()

        if self.shipping_fee != 0:
            print("adding shipping fee")
            total += self.shipping_fee

        if self.pickup_fee != 0:
            print("adding pickup fee")
            total += self.pickup_fee

        if self.return_fee != 0:
            print("adding return fee")
            total += self.return_fee

        return total


class RentalPayment(models.Model):
    txn_code = models.CharField(max_length=50)
    user = models.ForeignKey(
        "users.Profile", on_delete=models.SET_NULL, blank=True, null=True
    )
    amount = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.txn_code}"


class RentalRefund(models.Model):
    que = models.ForeignKey(RentalQue, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class RentalWebhookBackup(models.Model):
    pay_sol = models.CharField(max_length=500, blank=True, null=True)
    the_que = models.ForeignKey(
        RentalQue, on_delete=models.CASCADE, blank=True, null=True
    )
    req_body = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.pay_sol
