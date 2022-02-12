from rest_framework import serializers
from django.conf import settings
import importlib

from rentals.models import RentalPlatform, RentalCat, RentalGame, RentalGameTrailer


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


class RentalGameTrailerSerializer(serializers.ModelSerializer):
    platform = RentalPlatformSerializer()

    class Meta:
        model = RentalGameTrailer
        fields = "__all__"
