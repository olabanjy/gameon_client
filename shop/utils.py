import json
from .models import *

from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model


def cookieCart(request):

    # Create empty cart for now for non-logged in user
    try:
        cart = json.loads(request.COOKIES["cart"])
    except:
        cart = {}
        print("CART:", cart)

    items = []
    order = {"get_total": 0, "get_cart_items": 0}
    cartItems = order["get_cart_items"]

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:
            cartItems += cart[i]["quantity"]

            product = Item.objects.get(id=i)
            total = product.price * cart[i]["quantity"]

            order["get_total"] += total
            order["get_cart_items"] += cart[i]["quantity"]

            item = {
                "id": product.id,
                "item": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "displayImagePath": product.displayImagePath,
                },
                "quantity": cart[i]["quantity"],
                "get_final_price": total,
            }
            items.append(item)

        except:
            pass

    return {"cartItems": cartItems, "order": order, "items": items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.profile
        order, created = Order.objects.get_or_create(user=customer, ordered=False)
        items = order.items.all()
        qty = 0
        for order_item in order.items.all():
            qty += order_item.quantity
        cartItems = qty
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData["cartItems"]
        order = cookieData["order"]
        items = cookieData["items"]

    return {"cartItems": cartItems, "order": order, "items": items}


def guestOrder(request, data):
    first_name = data["userInfo"]["first_name"]
    last_name = data["userInfo"]["last_name"]
    phone = data["userInfo"]["phone"]
    user_email = data["userInfo"]["email"]

    shipping_address = data["shippingInfo"]["shipping_address"]
    shipping_address2 = data["shippingInfo"]["shipping_address2"]
    shipping_city = data["shippingInfo"]["shipping_city"]
    shipping_state = data["shippingInfo"]["shipping_state"]

    billing_address = data["billingInfo"]["billing_address"]
    billing_address2 = data["billingInfo"]["billing_address2"]
    billing_city = data["billingInfo"]["billing_city"]
    billing_state = data["billingInfo"]["billing_state"]

    cookieData = cookieCart(request)
    items = cookieData["items"]

    user_password = f"{user_email.split('@', 1)[0]}{1234}"
    # User = get_user_model
    the_user, created = User.objects.get_or_create(
        username=str(user_email.split("@", 1)[0]),
        defaults={"email": user_email, "password": make_password(user_password)},
    )

    the_profile, created = Profile.objects.get_or_create(user=the_user)

    # send welcome email to user

    guest_shipping_address = Address.objects.create(
        user=the_profile,
        street_address=shipping_address,
        apartment_address=shipping_address2,
        city=shipping_city,
        state=shipping_state,
        address_type="S",
    )

    guest_billing_address = Address.objects.create(
        user=the_profile,
        street_address=billing_address,
        apartment_address=billing_address2,
        city=billing_city,
        state=billing_state,
        address_type="B",
    )

    order = Order.objects.create(
        user=the_profile,
        ordered=False,
        shipping_address=guest_shipping_address,
        billing_address=guest_billing_address,
    )

    for item in items:
        the_item = Item.objects.get(id=item["id"])
        order_item, created = OrderItem.objects.get_or_create(
            item=the_item, user=the_profile, quantity=item["quantity"], ordered=False
        )
        order.items.add(order_item)
    print("finished processing guest order")
    return the_profile, order
