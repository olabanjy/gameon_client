from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
import secrets, datetime, pytz

from .serializers import (
    ItemPlatformSerializer,
    ItemCatSerializer,
    ItemTypeSerializer,
    ItemSerializer,
)

from shop.models import ItemPlatform, ItemCat, ItemType, Item, OrderItem

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
