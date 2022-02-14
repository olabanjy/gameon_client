from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
import secrets, datetime, pytz
from distutils.util import strtobool

from .serializers import (
    ItemPlatformSerializer,
    ItemCatSerializer,
    ItemTypeSerializer,
    ItemSerializer,
    OrderSerializer,
)

from shop.models import ItemPlatform, ItemCat, ItemType, Item, OrderItem, Order

from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import render

from django.conf import settings
from django.shortcuts import render, HttpResponse
from django.http import JsonResponse

from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from django.utils import datetime_safe, timezone


import requests, json


class ItemPlatformViewSet(ModelViewSet):
    queryset = ItemPlatform.objects.all()
    serializer_class = ItemPlatformSerializer

    def list(self, request):
        serializer = ItemPlatformSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def admin_create_plat(self, request):
        try:
            new_plat, created = ItemPlatform.objects.get_or_create(
                name=request.data["name"],
                desc=request.data["slug"],
                iconImagePath=request.data["iconImagePath"],
            )

            serializer = self.get_serializer(new_plat)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class ItemCatViewSet(ModelViewSet):
    queryset = ItemCat.objects.all()
    serializer_class = ItemCatSerializer

    def list(self, request):
        serializer = ItemCatSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemTypeViewSet(ModelViewSet):
    queryset = ItemType.objects.all()
    serializer_class = ItemTypeSerializer

    def list(self, request):
        serializer = ItemTypeSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ItemsViewSet(ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    def list(self, request):
        serializer = ItemSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def admin_create_item(self, request):
        try:
            the_platform = ItemPlatform.objects.get(id=int(request.data["platformId"]))
        except ItemPlatform.DoesNotExist:
            return Response(
                {"platformId": ["Platform does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_item, created = Item.objects.get_or_create(
                name=request.data["name"],
                platform=the_platform,
                numberInStock=int(request.data["numberInStock"]),
                dailyRentalRate=int(request.data["dailyRentalRate"]),
                featured=bool(strtobool(request.data["featured"])),
            )

            if request.data.get("displayImagePath"):
                new_item.displayImagePath = request.data["displayImagePath"]
            if request.data.get("thumbnailImagePath"):
                new_item.thumbnailImagePath = request.data["thumbnailImagePath"]
            if request.data.get("bannerImagePath"):
                new_item.bannerImagePath = request.data["bannerImagePath"]

            new_item.save()

            serializer = self.get_serializer(new_item)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.filter(ordered=True).all()
    serializer_class = OrderSerializer

    def list(self, request):
        serializer = OrderSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def mark_as_delivered(self, request):
        order_id = request.data["id"]
        print(order_id)

        try:
            the_order = Order.objects.get(id=int(order_id))
            the_order.received = True
            the_order.save()
            print(the_order.received)
            serializer = self.get_serializer(the_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
