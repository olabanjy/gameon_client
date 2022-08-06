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
    RentalQueItems,
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


from django.core.files import File
from django.core.files.base import ContentFile

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
            print("name is", the_cat.name)
            if the_cat.desc == "no_category":
                return Response(
                    {"message": ["You cannot delete base category!"]},
                    status=status.HTTP_200_OK,
                )
            # reassign all products with category
            try:
                print("check", RentalGame.objects.filter(cat=the_cat).all())
                getNoCat = RentalCat.objects.filter(desc="no_category").first()
                print(getNoCat)
                print("git here")
                for prod in RentalGame.objects.filter(cat=the_cat).all():
                    print(prod)
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

            if request.data.get("desc"):
                the_game.desc = request.data["desc"]

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

            if request.data.get("desc"):
                new_item.desc = request.data["desc"]

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

    @action(methods=["POST"], detail=False)
    def admin_vendor_create_item(self, request):
        try:
            new_item, created = RentalGame.objects.get_or_create(
                name=request.data["name"],
                numberInStock=int(request.data["numberInStock"]),
                dailyRentalRate=int(request.data["dailyRentalRate"]),
            )
            if request.data.get("catName"):

                theCat = RentalCat.objects.filter(
                    name__in=request.data["catName"]
                ).first()
                new_item.cat.add(theCat)

            if request.data.get("desc"):
                new_item.desc = request.data["desc"]
            if request.data.get("discount_price"):

                new_item.discount_price = request.data["discount_price"]

            if request.data.get("vendor"):
                new_item.vendor = request.data["vendor"]

            if request.data.get("vendor_code"):
                new_item.vendor_code = request.data["vendor_code"]
                new_item.adminOwned = False

            new_item.save()

            if request.data.get("displayImagePath"):
                fetch_display_img = requests.get(request.data["displayImagePath"])
                if fetch_display_img.status_code == 200:
                    data = fetch_display_img.content
                    filename = request.data["displayImagePath"].split("/")[-1]
                    new_item.displayImagePath.save(filename, ContentFile(data))

                else:
                    print(fetch_thumbnail_img)
            if request.data.get("thumbnailImagePath"):
                # new_item.thumbnailImagePath = request.data["thumbnailImagePath"]
                fetch_thumbnail_img = requests.get(request.data["thumbnailImagePath"])
                if fetch_thumbnail_img.status_code == 200:
                    data = fetch_thumbnail_img.content
                    filename = request.data["thumbnailImagePath"].split("/")[-1]
                    new_item.thumbnailImagePath.save(filename, ContentFile(data))

                else:
                    print(fetch_thumbnail_img)
            if request.data.get("bannerImagePath"):
                # new_item.bannerImagePath = request.data["bannerImagePath"]

                fetch_banner_img = requests.get(request.data["bannerImagePath"])
                if fetch_banner_img.status_code == 200:
                    data = fetch_thumbnail_img.content
                    filename = request.data["bannerImagePath"].split("/")[-1]
                    new_item.bannerImagePath.save(filename, ContentFile(data))

                else:
                    print(fetch_thumbnail_img)

            new_item.save()

            serializer = self.get_serializer(new_item)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
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

    @action(methods=["GET"], detail=False)
    def get_vendor_orders(self, request):
        try:
            vendor_code = request.GET.get("vendor_code", None)

            if vendor_code is None:
                return Response(
                    {"message": "Vendor code needed to fetch orders"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            vendorItems = RentalQueItems.objects.filter(item__vendor_code=vendor_code)
            if vendorItems.exists():
                print(vendorItems)
                serializer = RentalQueItemsSerializer(vendorItems, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"message": "Vendor code needed to fetch orders"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            print("error", e)
            return Response(
                {"message": e},
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
            new_trailer, created = RentalGameTrailer.objects.get_or_create(
                name=request.data["name"],
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
