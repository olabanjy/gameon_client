from rest_framework.views import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers, status
from rest_framework.decorators import action
import secrets, datetime, pytz
from distutils.util import strtobool

from .serializers import (
    RentalPlatformSerializer,
    RentalGameSerializer,
    RentalCatSerializer,
    TrailerSerializer,
    RentalQueSerializer,
    RentalQueItemsSerializer,
    AddressSerializer,
)

from rentals.models import (
    RentalQue,
    RentalPlatform,
    RentalCat,
    RentalGame,
    RentalGameTrailer,
)

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
    def admin_delete_plat(self, request):
        try:
            the_platform = RentalPlatform.objects.get(
                id=int(request.data["platformId"])
            )
            the_platform.delete()
            return Response(
                {"message": ["Platform deleted "]},
                status=status.HTTP_200_OK,
            )

        except RentalPlatform.DoesNotExist:
            return Response(
                {"platformId": ["Platform does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

    @action(methods=["POST"], detail=False)
    def admin_create_cat(self, request):
        try:
            new_cat, created = RentalCat.objects.get_or_create(
                name=request.data["name"],
                desc=request.data["slug"],
                iconImagePath=request.data["iconImagePath"],
            )

            serializer = self.get_serializer(new_cat)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def admin_delete_cat(self, request):
        try:

            the_cat = RentalCat.objects.get(id=int(request.data["catId"]))
            if the_cat.desc == "no_category":
                return Response(
                    {"message": ["You cannot delete base category!"]},
                    status=status.HTTP_200_OK,
                )
            # reassign all products with category
            try:
                getNoCat = RentalCat.objects.filter(desc="no_category").first()
                for prod in RentalGame.objects.filter(cat=the_cat).all():
                    prod.cat.remove(the_cat)
                    prod.cat.add(getNoCat)
                    prod.save()
            except Exception as e:
                print("error", e)
                pass
            the_cat.delete()
            return Response(
                {"message": ["Category deleted "]},
                status=status.HTTP_200_OK,
            )

        except RentalCat.DoesNotExist:
            return Response(
                {"catId": ["Category does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RentalGamesViewSet(ModelViewSet):
    queryset = RentalGame.objects.all()
    serializer_class = RentalGameSerializer

    def list(self, request):
        serializer = RentalGameSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def admin_delete_item(self, request):
        try:
            the_item = RentalGame.objects.get(id=int(request.data["id"]))
            the_item.delete()
            return Response(
                {"message": ["Rental Game deleted "]},
                status=status.HTTP_200_OK,
            )

        except RentalGame.DoesNotExist:
            return Response(
                {"message": ["Game does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["POST"], detail=False)
    def update_rental_game(self, request):
        try:
            the_game = RentalGame.objects.get(id=int(request.data["id"]))
        except RentalGame.DoesNotExist:
            return Response(
                {"message": ["The selected Game does not exist!"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            if request.data.get("catId"):
                for val in request.data["catId"]:
                    theCat = RentalCat.objects.get(id=int(val))

                    the_game.cat.add(theCat)
            if request.data.get("name"):
                the_game.name = request.data["name"]

            if request.data.get("numberInStock"):
                the_game.numberInStock = request.data["numberInStock"]

            if request.data.get("dailyRentalRate"):
                the_game.dailyRentalRate = request.data["dailyRentalRate"]

            if request.data.get("featured"):
                the_game.featured = bool(strtobool(request.data["featured"]))

            if "displayImagePath" in request.FILES:
                the_game.displayImagePath = request.FILES["displayImagePath"]

            if "thumbnailImagePath" in request.FILES:
                the_game.thumbnailImagePath = request.FILES["thumbnailImagePath"]

            if "bannerImagePath" in request.FILES:
                the_game.bannerImagePath = request.FILES["bannerImagePath"]

            the_game.save()

            serializer = self.get_serializer(the_game)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def admin_create_item(self, request):

        try:
            new_item, created = RentalGame.objects.get_or_create(
                name=request.data["name"],
                numberInStock=int(request.data["numberInStock"]),
                dailyRentalRate=int(request.data["dailyRentalRate"]),
                featured=bool(strtobool(request.data["featured"])),
            )

            if request.data.get("catId"):
                for val in request.data["catId"]:
                    theCat = RentalCat.objects.get(id=int(val))

                    new_item.cat.add(theCat)

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
    queryset = RentalQue.objects.all()
    serializer_class = RentalQueSerializer

    def list(self, request):
        serializer = RentalQueSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def get_que_details(self, request):
        try:
            the_que = RentalQue.objects.get(id=int(request.data["id"]))
            serializer = self.get_serializer(the_que)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RentalQue.DoesNotExist:
            return Response(
                {"message": "Rental Order Does not Exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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


class TrailersViewSet(ModelViewSet):
    queryset = RentalGameTrailer.objects.all()
    serializer_class = TrailerSerializer

    def list(self, request):
        serializer = TrailerSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def admin_create_trailer(self, request):
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
            new_trailer, created = RentalGameTrailer.objects.get_or_create(
                name=request.data["name"],
                platform=the_platform,
                trailer_banner=request.FILES["trailerBanner"],
                trailer_yt_link=request.data["yt_url"],
                highlight_title=request.data["title"],
            )

            if request.data.get("desc"):
                new_trailer.highlight_desc = request.data["desc"]

            new_trailer.save()

            serializer = self.get_serializer(new_trailer)

            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def admin_delete_trailer(self, request):
        try:
            the_trailer = RentalGameTrailer.objects.get(id=int(request.data["id"]))
            the_trailer.delete()
            return Response(
                {"message": ["Trailer deleted "]},
                status=status.HTTP_200_OK,
            )

        except RentalGameTrailer.DoesNotExist:
            return Response(
                {"message": ["Trailer does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
