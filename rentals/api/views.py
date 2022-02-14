from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
import secrets, datetime, pytz
from distutils.util import strtobool

from rentals.models import RentalQue
from .serializers import (
    RentalPlatformSerializer,
    RentalGameSerializer,
    RentalCatSerializer,
    RentalGameTrailerSerializer,
    RentalQueSerializer,
    RentalQueItemsSerializer,
    AddressSerializer,
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

    @action(methods=["POST"], detail=False)
    def admin_create_plat(self, request):
        try:
            new_plat, created = RentalPlatform.objects.get_or_create(
                name=request.data["name"],
                desc=request.data["slug"],
                iconImagePath=request.data["iconImagePath"],
            )

            serializer = self.get_serializer(new_plat)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


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

    @action(methods=["POST"], detail=False)
    def admin_create_item(self, request):
        try:
            the_platform = RentalPlatform.objects.get(
                id=int(request.data["platformId"])
            )
        except RentalPlatform.DoesNotExist:
            return Response(
                {"platformId": ["Platform does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            new_item, created = RentalGame.objects.get_or_create(
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


class RentalQueViewSet(ModelViewSet):
    queryset = RentalQue.objects.filter(ordered=True).all()
    serializer_class = RentalQueSerializer

    def list(self, request):
        serializer = RentalQueSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def mark_as_delivered(self, request):
        que_id = request.data["id"]
        print(que_id)

        try:
            the_que = RentalQue.objects.get(id=int(que_id))
            the_que.received = True
            the_que.save()
            print(the_que.received)

            serializer = self.get_serializer(the_que)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
