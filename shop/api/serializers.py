from rest_framework import serializers
from django.conf import settings
import importlib

from shop.models import ItemPlatform, ItemCat, ItemType, Item, OrderItem


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
