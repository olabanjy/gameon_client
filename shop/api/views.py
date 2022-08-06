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
    OrderItemsSerializer,
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

from django.core.files import File
from django.core.files.base import ContentFile
import requests, json
import shutil


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

    @action(methods=["POST"], detail=False)
    def admin_create_cat(self, request):
        try:
            new_cat, created = ItemCat.objects.get_or_create(
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
            the_cat = ItemCat.objects.get(id=int(request.data["catId"]))
            print("name is", the_cat.name)
            if the_cat.desc == "no_category":
                return Response(
                    {"message": ["You cannot delete base category!"]},
                    status=status.HTTP_200_OK,
                )
            # reassign all products with category
            try:
                print("check", Item.objects.filter(cat=the_cat).all())
                getNoCat = ItemCat.objects.filter(desc="no_category").first()
                print(getNoCat)
                print("git here")
                for prod in Item.objects.filter(cat=the_cat).all():
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

        except ItemCat.DoesNotExist:
            return Response(
                {"catId": ["Category does not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
    def admin_delete_item(self, request):
        try:
            the_item = Item.objects.get(id=int(request.data["id"]))
            the_item.delete()
            return Response(
                {"message": ["Shop Item deleted "]},
                status=status.HTTP_200_OK,
            )

        except Item.DoesNotExist:
            return Response(
                {"message": ["Shop Item not exist"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=["POST"], detail=False)
    def update_shop_item(self, request):
        try:
            the_item = Item.objects.get(id=int(request.data["id"]))
        except Item.DoesNotExist:
            return Response(
                {"message": ["The selected Item does not exist!"]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:

            if request.data.get("name"):
                the_item.name = request.data["name"]

            if request.data.get("numberInStock"):
                the_item.numberInStock = request.data["numberInStock"]

            if request.data.get("price"):
                the_item.price = request.data["price"]

            if request.data.get("desc"):
                the_item.desc = request.data["desc"]

            if request.data.get("discount_price"):
                the_item.discount_price = request.data["discount_price"]

            if request.data.get("featured"):
                the_item.featured = bool(strtobool(request.data["featured"]))

            if "displayImagePath" in request.FILES:
                the_item.displayImagePath = request.FILES["displayImagePath"]

            if "thumbnailImagePath" in request.FILES:
                the_item.thumbnailImagePath = request.FILES["thumbnailImagePath"]

            if "bannerImagePath" in request.FILES:
                the_item.bannerImagePath = request.FILES["bannerImagePath"]

            the_item.save()

            serializer = self.get_serializer(the_item)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def admin_create_item(self, request):
        try:
            new_item, created = Item.objects.get_or_create(
                name=request.data["name"],
                numberInStock=int(request.data["numberInStock"]),
                price=int(request.data["price"]),
                featured=bool(strtobool(request.data["featured"])),
            )
            if request.data.get("catId"):
                for val in request.data["catId"]:
                    theCat = ItemCat.objects.get(id=int(val))
                    new_item.cat.add(theCat)
            if request.data.get("discount_price"):
                new_item.discount_price = request.data["discount_price"]

            if request.data.get("desc"):
                new_item.desc = request.data["desc"]

            if request.data.get("displayImagePath"):
                new_item.displayImagePath = request.data["displayImagePath"]
            if request.data.get("thumbnailImagePath"):
                new_item.thumbnailImagePath = request.data["thumbnailImagePath"]
            if request.data.get("bannerImagePath"):
                new_item.bannerImagePath = request.data["bannerImagePath"]

            if request.data.get("vendor"):
                new_item.vendor = request.data["vendor"]

            if request.data.get("vendor_code"):
                new_item.vendor_code = request.data["vendor_code"]
                new_item.adminOwned = False

            new_item.save()

            serializer = self.get_serializer(new_item)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["POST"], detail=False)
    def admin_vendor_create_item(self, request):
        try:
            new_item, created = Item.objects.get_or_create(
                name=request.data["name"],
                numberInStock=int(request.data["numberInStock"]),
                price=int(request.data["price"]),
            )
            if request.data.get("catName"):

                theCat = ItemCat.objects.filter(
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


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.filter(ordered=True).all()
    serializer_class = OrderSerializer

    def list(self, request):
        serializer = OrderSerializer(
            self.queryset, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False)
    def get_order_details(self, request):
        try:
            order = Order.objects.get(id=int(request.data["id"]))
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response(
                {"message": "Sales Order Does not Exist"},
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
            vendorItems = OrderItem.objects.filter(item__vendor_code=vendor_code)
            if vendorItems.exists():
                print(vendorItems)
                serializer = OrderItemsSerializer(vendorItems, many=True)
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
