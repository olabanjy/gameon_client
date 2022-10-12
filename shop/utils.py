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
    order = {"get_order_total": 0, "get_cart_items": 0}
    cartItems = order["get_cart_items"]

    # vendorList = []
    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        try:

            cartItems += cart[i]["quantity"]

            product = Item.objects.get(id=i)
            total = product.price * cart[i]["quantity"]

            order["get_order_total"] += total
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

            # if product.vendor_code not in vendorList:
            #     vendorList.append(product.vendor_code)

        except:
            pass

    # if len(vendorList) == 1:
    #     order.update(
    #         {
    #             "instant_delivery_eligible": True,
    #             "instant_delivery_vendor": vendorList[0],
    #         }
    #     )
    print(order)

    return {"cartItems": cartItems, "order": order, "items": items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.profile

        order_qs = Order.objects.filter(user=customer, ordered=False)
        if order_qs.exists():
            order = order_qs.last()
            items = order.items.all()
            qty = 0
            # cartVendorList = []
            for order_item in order.items.all():
                qty += order_item.quantity
                # if order_item.item.vendor_code not in cartVendorList:
                #     cartVendorList.append(order_item.item.vendor_code)

            cartItems = qty
            # check if order is single vendor
            # if len(cartVendorList) == 1:
            #     order.instant_delivery_eligible = True
            #     order.instant_delivery_vendor = cartVendorList[0]
            #     order.save()
            # print(order.instant_delivery_eligible)

        else:
            order, created = Order.objects.get_or_create(user=customer, ordered=False)
            items = order.items.all()
            qty = 0
            # cartVendorList = []
            for order_item in order.items.all():
                qty += order_item.quantity
                # if order_item.item.vendor_code not in cartVendorList:
                #     cartVendorList.append(order_item.item.vendor_code)
            cartItems = qty
            # if len(cartVendorList) == 1:
            #     order.instant_delivery_eligible = True
            #     order.instant_delivery_vendor = cartVendorList[0]
            #     order.save()
            # print(order.instant_delivery_eligible)

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
    # shipping_address2 = data["shippingInfo"]["shipping_address2"]
    shipping_city = data["shippingInfo"]["shipping_city"]
    shipping_area = data["shippingInfo"]["shipping_area"]

    billing_address = data["billingInfo"]["billing_address"]
    # billing_address2 = data["billingInfo"]["billing_address2"]
    billing_city = data["billingInfo"]["billing_city"]
    billing_state = data["billingInfo"]["billing_state"]

    cookieData = cookieCart(request)
    items = cookieData["items"]

    user_password = f"{user_email.split('@', 1)[0]}{1234}"
    # User = get_user_model
    try:
        the_user = User.objects.get(email=user_email)
        print("this user exists as", the_user)
    except User.DoesNotExist:
        the_user, created = User.objects.get_or_create(
            username=str(user_email.split("@", 1)[0]),
            defaults={"email": user_email, "password": make_password(user_password)},
        )
        # send an email to the user here!

    the_profile, created = Profile.objects.get_or_create(user=the_user)

    # send welcome email to user

    guest_shipping_address = Address.objects.create(
        user=the_profile,
        street_address=shipping_address,
        region=shipping_area,
        # apartment_address=shipping_address2,
        city=shipping_city,
        state="Lagos State",
        address_type="S",
    )

    guest_billing_address = Address.objects.create(
        user=the_profile,
        street_address=billing_address,
        # apartment_address=billing_address2,
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

    # if "lagos" in shipping_state.lower():
    #     order.shipping_fee = 3000
    # else:
    #     order.shipping_fee = 5000

    shipping_fee = 0
    for region in settings.ADDRESS_REGIONS:
        if region["slug"] == shipping_area:
            print(region["price"])
            shipping_fee = int(region["price"])

    print(shipping_fee)
    try:
        order.shipping_fee = 0
        order.save()
    except:
        pass
    order.shipping_fee = shipping_fee

    order.save()
    print(order.get_total())

    for item in items:
        the_item = Item.objects.get(id=item["id"])
        order_item, created = OrderItem.objects.get_or_create(
            item=the_item, user=the_profile, quantity=item["quantity"], ordered=False
        )
        order.items.add(order_item)
    print("finished processing guest order")
    return the_profile, order


def confirmInstantDeliveryFare(data):
    try:
        pass
    except Exception as e:
        print("error", e)
        pass
