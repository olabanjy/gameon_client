from rest_framework import serializers
from django.conf import settings
import importlib

from shop.models import ItemPlatform, ItemCat, ItemType, Item, OrderItem, Order

from users.models import Address, Profile
from users.api.serializers import ProfileSerializer
from django.contrib.humanize.templatetags.humanize import naturalday


class ItemPlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPlatform
        fields = "__all__"


class ItemCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCat
        fields = "__all__"


class ItemTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemType
        fields = "__all__"


class ItemSerializer(serializers.ModelSerializer):
    platform = ItemPlatformSerializer()
    cat = ItemCatSerializer()
    type = ItemTypeSerializer()

    class Meta:
        model = Item
        fields = "__all__"


class OrderItemsSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "ordered",
            "item",
            "quantity",
            "final_price",
        ]

    def get_final_price(self, object):

        if object.item.discount_price:
            return object.get_total_discount_item_price()
        return object.get_final_price()


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


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(read_only=True, many=True)
    user = ProfileSerializer()
    shipping_address = AddressSerializer()
    billing_address = AddressSerializer()
    order_total = serializers.SerializerMethodField()
    ordered_date = serializers.SerializerMethodField()

    class Meta:
        model = Order
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
            "order_total",
        ]

    def get_order_total(self, object):
        total = 0
        for que_item in object.items.all():
            total += que_item.get_final_price()
        return total

    def get_ordered_date(self, object):
        return naturalday(object.ordered_date)
