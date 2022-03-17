from ast import Add
from rest_framework import serializers
from django.conf import settings
import importlib

from rentals.models import (
    RentalPlatform,
    RentalCat,
    RentalGame,
    RentalGameTrailer,
    RentalQue,
    RentalPayment,
    RentalQueItems,
    RentalRefund,
)
from users.models import Address, Profile
from users.api.serializers import ProfileSerializer
from django.contrib.humanize.templatetags.humanize import naturalday


class RentalPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalPlatform
        fields = ["id", "name", "desc", "iconImagePath"]


class RentalCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentalCat
        fields = "__all__"


class RentalGameSerializer(serializers.ModelSerializer):
    platform = RentalPlatformSerializer()
    cat = RentalCatSerializer()

    class Meta:
        model = RentalGame
        fields = "__all__"


# class RentalGameTrailerSerializer(serializers.ModelSerializer):
#     platform = RentalPlatformSerializer()

#     class Meta:
#         model = RentalGameTrailer
#         fields = "__all__"


class RentalQueItemsSerializer(serializers.ModelSerializer):
    item = RentalGameSerializer()
    # final_price = serializers.SerializerMethodField()

    class Meta:
        model = RentalQueItems
        fields = [
            "ordered",
            "item",
            "quantity",
            "from_date",
            "to_date",
            "no_of_days",
        ]

    # def get_final_price(self, object):
    #     return (object.quantity * object.item.dailyRentalRate) * object.no_of_days


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            "street_address",
            "apartment_address",
            "city",
            "state",
            "address_type",
            "default",
        ]


class RentalQueSerializer(serializers.ModelSerializer):
    items = RentalQueItemsSerializer(read_only=True, many=True)
    user = ProfileSerializer()
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()
    que_total = serializers.SerializerMethodField()
    ordered_date = serializers.SerializerMethodField()

    class Meta:
        model = RentalQue
        fields = [
            "id",
            "user",
            "ref_code",
            "items",
            "start_date",
            "ordered_date",
            "ordered",
            "shipping_address",
            "billing_address",
            "shipping_fee",
            "being_delivered",
            "received",
            "refund_requested",
            "refund_granted",
            "que_total",
        ]

    def get_que_total(self, object):
        total = 0
        for que_item in object.items.all():
            total += que_item.get_final_price()
        return total

    def get_ordered_date(self, object):
        return naturalday(object.ordered_date)


class TrailerSerializer(serializers.ModelSerializer):
    platform = RentalPlatformSerializer(read_only=True)

    class Meta:
        model = RentalGameTrailer
        fields = [
            "id",
            "name",
            "platform",
            "trailer_banner",
            "trailer_yt_link",
            "highlight_title",
            "highlight_desc",
            "views",
            "created_at",
        ]
