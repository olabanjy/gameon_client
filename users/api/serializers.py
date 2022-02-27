from rest_framework import serializers
from users.models import *
from django.contrib.auth.models import User
from datetime import datetime
from django.utils.timesince import timesince


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("id",)


class UserKYCSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserKYC
        fields = [
            "id",
            "id_type",
            "id_unique_number",
            "photo",
            "photo_2",
            "status",
            "verified",
            "verified_at",
            "created_at",
        ]


class AddressVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressVerification
        fields = [
            "id",
            "id_type",
            "photo",
            "status",
            "verified",
            "verified_at",
            "created_at",
        ]


class BasicUserAddressSerializer(serializers.ModelSerializer):
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


class ProfileSerializer(serializers.ModelSerializer):
    time_joined = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()
    user_kyc = UserKYCSerializer(many=True, read_only=True)
    user_prim_address = serializers.SerializerMethodField()
    user_address_verification = AddressVerificationSerializer(many=True, read_only=True)

    class Meta:
        model = Profile
        exclude = ("user",)

    def get_time_joined(self, object):
        created_at = object.created_at
        time_delta = created_at.strftime("%Y-%m-%d %H:%M")
        return time_delta

    def get_last_login(self, object):
        the_last_login = object.last_login
        return the_last_login

    def get_user_email(self, object):
        return object.user.email

    def get_user_prim_address(self, object):
        user_add_obj = Address.objects.filter(user=object, address_type="P")
        if user_add_obj.exists():
            user_add = user_add_obj.first()
            return BasicUserAddressSerializer(user_add).data
        return None
