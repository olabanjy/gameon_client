import json
from .models import *

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


def queData(request):
    if request.user.is_authenticated:
        customer = request.user.profile

        que, created = RentalQue.objects.get_or_create(user=customer, ordered=False)
        print(que)

        qty = 0

        # if que.items
        items = que.items.all()
        for que_item in que.items.all():
            qty += que_item.quantity
        cartItems = qty
    else:
        cartItems = 0
        que = None
        items = None

    return {"cartItems": cartItems, "order": que, "items": items}


# from geopy.distance import geodesic

# def calculate_item_distance(origin, dest):
# origin = (30.172705, 31.526725)  # (latitude, longitude) don't confuse
# dist = (30.288281, 31.732326)
