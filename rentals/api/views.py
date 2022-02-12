from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
import secrets, datetime, pytz

from .serializers import (
    RentalPlatformSerializer,
    RentalGameSerializer,
    RentalCatSerializer,
    RentalGameTrailerSerializer,
)

from rentals.models import RentalPlatform, RentalCat, RentalGame, RentalGameTrailer

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


class RentalPlatformViewSet(ModelViewSet):
    queryset = RentalPlatform.objects.all()
    serializer_class = RentalPlatformSerializer

    def list(self, request):
        serializer = RentalPlatformSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class RentalCatViewSet(ModelViewSet):
    queryset = RentalCat.objects.all()
    serializer_class = RentalCatSerializer

    def list(self, request):
        serializer = RentalCatSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class RentalGamesViewSet(ModelViewSet):
    queryset = RentalGame.objects.all()
    serializer_class = RentalGameSerializer

    def list(self, request):
        serializer = RentalGameSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
