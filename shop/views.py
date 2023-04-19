from django import template
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import JsonResponse
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.db.models import Sum
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from django.template import RequestContext, context
from django.utils.encoding import force_bytes
from paypal.standard.forms import PayPalPaymentsForm
from .models import *
from rentals.models import RentalGameTrailer
from .forms import *
from .utils import cookieCart, cartData, guestOrder
import json
import random
import string
import requests
from decimal import Decimal
import hmac
import hashlib

from rentals.models import RentalGame


# Create your views here.


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


def search_result(request):

    if request.is_ajax():
        res = None
        query = request.POST.get("query")
        print(query)
        # change this to icontains.dinstict in prod
        qs = Item.objects.filter(name__icontains=query)
        # print(qs)
        # this is for rental,  come back and fix shop
        rentalqs = RentalGame.objects.filter(name__icontains=query)
        print(rentalqs)
        # data = {"item": query}
        if len(rentalqs) > 0 and len(query) > 0:

            data = []
            for prod in rentalqs:
                item = {
                    "pk": prod.pk,
                    "name": prod.name,
                    "url": prod.get_absolute_url(),
                    "thumbnail": prod.thumbnailImagePath.url,
                    "price": f"{prod.dailyRentalRate}/day",
                }
                if item not in data:
                    data.append(item)

                print("list is", data)
                res = data

        else:
            res = "No items match your query! "
        return JsonResponse({"data": res})

    return JsonResponse({})


def shopHome(request):

    location_pulled = False
    template = "shop/shopHome.html"

    get_category = request.GET.get("item_categories", None)

    loclong = request.GET.get("loclong", None)
    loclat = request.GET.get("loclat", None)

    featured_items = Item.objects.filter(featured=True).all()
    the_featured_banner = Item.objects.filter(featured_banner=True).last()
    trailers = RentalGameTrailer.objects.all().order_by("created_at")[:4]
    showing_cat = "All categories"

    all_items = Item.objects.none()

    if loclat is not None and loclong is not None:
        dest = (loclat, loclong)
        all_shop_items = Item.objects.all().order_by("-created_at")
        range_items_id = [o.id for o in all_shop_items if o.checkInRadius(dest) == True]
        all_items = all_shop_items.filter(id__in=range_items_id)
        location_pulled = True

    if get_category is not None:

        if get_category != "all":
            the_cat = ItemCat.objects.get(name=get_category)
            all_items = all_items.filter(cat=the_cat).all().order_by("-created_at")
            showing_cat = the_cat.name

    page = request.GET.get("page", 1)
    paginator = Paginator(all_items, 15)

    try:
        all_items = paginator.page(page)
    except PageNotAnInteger:
        all_items = paginator.page(1)
    except EmptyPage:
        all_items = paginator.page(paginator.num_pages)

    # platforms = ItemPlatform.objects.all()
    cats = ItemCat.objects.all()

    context = {
        "featured_items": featured_items,
        "all_items": all_items,
        "the_featured_banner": the_featured_banner,
        "trailers": trailers,
        # "platforms": platforms,
        "cats": cats,
        "showing_cat": showing_cat,
        # "showing_plat": showing_plat,
        "location_pulled": location_pulled,
    }

    return render(request, template, context)


def itemDetail(request, item_id):
    template = "shop/item_details.html"
    item = Item.objects.get(id=item_id)
    all_items = Item.objects.all().exclude(id=item_id)[:10]
    print(item)
    context = {"item": item, "all_items": all_items}
    return render(request, template, context)


def cart(request):

    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    print(order)

    context = {"items": items, "order": order}

    return render(request, "shop/cart.html", context)


def process_checkout(request):

    data = json.loads(request.body)
    print(data)

    if request.user.is_authenticated:
        the_profile = request.user.profile
        pickup_option = data["shippingInfo"]["pickup_option"]
        billing_address = data["billingInfo"]["billing_address"]
        billing_city = data["billingInfo"]["billing_city"]
        billing_state = data["billingInfo"]["billing_state"]
        try:
            order = Order.objects.filter(
                user=the_profile, ordered=False, items__isnull=False
            ).last()
            try:
                order.shipping_fee = 0
                order.save()
            except:
                pass
            if not order.billing_address:
                billing_address = Address.objects.create(
                    user=the_profile,
                    street_address=billing_address,
                    # apartment_address=billing_address2,
                    city=billing_city,
                    state=billing_state,
                    address_type="B",
                )
                order.billing_address = billing_address

            if pickup_option == "no_pickup":
                shipping_address = data["shippingInfo"]["shipping_address"]
                shipping_city = data["shippingInfo"]["shipping_city"]

                guest_shipping_address = Address.objects.create(
                    user=the_profile,
                    street_address=shipping_address,
                    city=shipping_city,
                    state="Lagos State",
                    address_type="S",
                )
                order.shipping_address = guest_shipping_address

                order.shipping_fee = 1500
            order.save()
        except ObjectDoesNotExist:
            print("You don not have any item in the cart")
            return redirect("shop:shop-home")

    else:
        the_profile, order = guestOrder(request, data)
        print(order.get_total())

    return JsonResponse(
        data={"the_profile_id": the_profile.pk, "the_order_id": order.pk},
    )
    # return JsonResponse()


def checkout(request):
    template = "shop/checkout.html"
    data = cartData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    if cartItems < 1:
        print("You don not have any item in the cart")
        return redirect("shop:shop-home")

    context = {
        "items": items,
        "order": order,
        "address_regions": settings.ADDRESS_REGIONS,
    }

    return render(request, template, context)


class PaymentView(View):
    def get(self, request, the_profile_id, the_order_id):
        template = "shop/payment.html"

        the_profile = Profile.objects.get(pk=the_profile_id)

        order = Order.objects.get(pk=the_order_id, ordered=False)
        print(order.get_order_total())
        print(order.get_total())
        if order.billing_address:

            host = self.request.get_host()

            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": "%.2f" % Decimal(order.get_total()).quantize(Decimal(".01")),
                "item_name": "Order {}".format(order.id),
                "invoice": str(order.id),
                "currency_code": "USD",
                "notify_url": "http://{}{}".format(host, reverse("paypal-ipn")),
                "return_url": "http://{}{}".format(
                    host, reverse("shop:paypal_payment_done")
                ),
                "cancel_return": "http://{}{}".format(
                    host, reverse("shop:paypal_payment_canceled")
                ),
            }

            paypal_form = PayPalPaymentsForm(initial=paypal_dict)

            context = {
                "order": order,
                "the_profile": the_profile,
                "paypal_form": paypal_form,
                "TEST_PAYSTACK_PUBLIC_KEY": settings.TEST_PAYSTACK_PUBLIC_KEY,
                "LIVE_PAYSTACK_PUBLIC_KEY": settings.LIVE_PAYSTACK_PUBLIC_KEY,
            }

            return render(self.request, template, context)

        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("shop:shop-checkout")

    def post(self, request, the_profile_id, the_order_id, *args, **kwargs):

        reference = self.request.POST.get("paystackToken")
        pay_method = self.request.POST.get("payment_type")

        order = Order.objects.get(pk=the_order_id, ordered=False)
        the_profile = Profile.objects.get(pk=the_profile_id)

        headers = {"Authorization": f"Bearer {settings.LIVE_PAYSTACK_PUBLIC_KEY}"}
        resp = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
        )
        response = resp.json()
        try:
            status = response["data"]["status"]
            auth_code = response["data"]["authorization"]["authorization_code"]
            if auth_code:
                print(auth_code)
            if status == "success":
                payment = Payment()
                payment.txn_code = reference
                payment.amount = int(order.get_total())
                payment.user = the_profile
                payment.save()

                order_items = order.items.all()
                order_item_total = 0
                for item in order_items:
                    item.ordered = True
                    item.save()

                    order_item_total += item.get_final_price()

                order.ordered = True
                order.payment = payment
                order.ref_code = create_ref_code()
                order.save()

                # send a successful card payment with receipt

                try:
                    subject, from_email, to = (
                        "YOUR ORDER IS ON THE WAY",
                        "GameOn <noreply@gameon.com.ng>",
                        [order.user.user.email],
                    )

                    html_content = render_to_string(
                        "events/sales_order_successfull.html",
                        {
                            "order_items": order_items,
                            "order_item_total": order_item_total,
                            "order": order,
                        },
                    )
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()

                except Exception as e:
                    print("error", e)
                    pass

                # send a mail to admin also

                try:
                    subject, from_email, to = (
                        "NEW SALES ORDER",
                        "GameOn <noreply@gameon.com.ng>",
                        ["admin@gameon.com.ng"],
                    )

                    html_content = render_to_string(
                        "events/new_sales_order_admin.html",
                        {
                            "order_items": order_items,
                            "order_item_total": order_item_total,
                            "order": order,
                            "email": order.user.user.email,
                        },
                    )
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()

                except:
                    pass

                messages.success(self.request, "Payment is successful")
                return redirect("shop:shop-home")
            else:
                messages.warning(self.request, "Payment failed")
                return HttpResponseRedirect(reverse("shop:shop-payment"))

        except (ValueError, NameError, TypeError) as error:
            err_msg = str(error)
            print(err_msg)
        except:
            print("Unexpected Error")
            raise


@csrf_exempt
def paypal_payment_done(request):

    # payment = Payment()
    # payment.txn_code = reference
    # payment.amount = int(order.get_total())
    # payment.user = the_profile
    # payment.save()

    # order_items = order.items.all()
    # # order_items.update(ordered=True)
    # for item in order_items:
    #     item.ordered = True
    #     item.save()

    # order.ordered = True
    # order.payment = payment
    # order.ref_code = create_ref_code()
    # order.save()
    return render(request, "shop/paypal_payment_done.html")


@csrf_exempt
def paypal_payment_canceled(request):
    return render(request, "shop/paypal_payment_canceled.html")


def update_item(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    print(productId, action)

    customer = request.user.profile
    product = Item.objects.get(id=productId)

    if action == "add":
        order_item_qs = OrderItem.objects.filter(
            item=product, user=customer, ordered=False
        )
        if not order_item_qs.exists():
            order_item = OrderItem.objects.create(
                item=product, user=customer, ordered=False
            )
        else:
            order_item = order_item_qs.last()
        order_qs = Order.objects.filter(user=customer, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item=product).exists():
                order_item.quantity += 1
                order_item.save()
                print("This item quantity was updated")
            else:
                order.items.add(order_item)
                print("This item was added to your cart")
        else:
            ordered_date = timezone.now()
            order = Order.objects.create(user=customer, ordered_date=ordered_date)
            order.items.add(order_item)
            print("This item was added to your cart")
    elif action == "remove":
        order_qs = Order.objects.filter(user=customer, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item=product).exists():
                order_item = OrderItem.objects.filter(
                    item=product, user=customer, ordered=False
                )[0]
                order.items.remove(order_item)
                order_item.delete()
                print("This item was removed from your cart")
            else:
                print("This item was not in ur cart")
        else:
            print("you do not have an active order")

    elif action == "remove-single":
        order_qs = Order.objects.filter(user=customer, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            # check if the order item is in the order
            if order.items.filter(item=product).exists():
                order_item = OrderItem.objects.filter(
                    item=product, user=customer, ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                print("The item was updated")
            else:
                print("This item was not in the cart")

        else:
            print("You do not have an active order")

    return JsonResponse("Item has been added to cart", safe=False)


@require_POST
@csrf_exempt
def paystack_test_webhook_view(request):
    print("This is an api webhook from paystack")
    new_wbh = WebhookBackup.objects.create(pay_sol="paystack")
    payload = json.loads(request.body)

    new_wbh.req_body = json.dumps(payload)
    new_wbh.save()

    paystack_sk = settings.TEST_PAYSTACK_SECRET_KEY

    computed_hmac = hmac.new(
        bytes(paystack_sk, "utf-8"),
        str.encode(request.body.decode("utf-8")),
        digestmod=hashlib.sha512,
    ).hexdigest()

    print(payload)

    sig_hash = request.headers.get("x-paystack-signature")

    if computed_hmac == sig_hash:
        reference = payload.get("data", {}).get("reference")
        if payload["event"] == "charge.success":
            user_email = payload["data"]["customer"]["email"]
            amount = payload["data"]["amount"]

            # check for the user
            the_user = User.objects.get(email=user_email)

            the_order_qs = Order.objects.filter(user=the_user.profile, ordered=False)
            if the_order_qs.exists():
                order = the_order_qs[0]
                # check order amount
                if order.get_total() == int(amount):
                    payment = Payment()
                    payment.txn_code = reference
                    payment.amount = int(order.get_total())
                    payment.user = the_user.profile
                    payment.save()

                    order_items = order.items.all()
                    # order_items.update(ordered=True)
                    for item in order_items:
                        item.ordered = True
                        item.save()

                    order.ordered = True
                    order.payment = payment
                    order.ref_code = create_ref_code()
                    order.save()

                    # send a successful card payment with receipt
                    return HttpResponse(status=200)

                else:
                    print("could not verify order amount")
                    # send help to shola or record to logs
                    new_app_log = AppLogs.objects.create(log_title="amount mismatch")
                    new_app_log.log = f"webhook body amount {int(amount)} does not match with order amount {order.get_total()}."
                    new_app_log.save()
                    return HttpResponse(status=200)
            else:
                print("payment already processed")
                return HttpResponse(status=200)
        else:
            return HttpResponse(status=200)

        return HttpResponse(status=200)
