from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
)
from django.http.response import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.db.models import Sum
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.template.loader import render_to_string
from django.template import RequestContext
from django.utils.encoding import force_bytes
from .models import *
from users.models import Address, Profile
from .utils import *
import json
import random
import string
import requests
from decimal import Decimal
import hmac
import hashlib
from django.views.defaults import page_not_found


def create_ref_code():
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=20))


def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid


# def error404(request, exception):
#     return page_not_found(request, exception, "errors/404.html")


def error404(request, exception):
    return render(request, "errors/404.html", status=404)


def error500(request):
    return render(request, "errors/500.html")


def rentalsHome(request):

    template = "rentals/rentalHome.html"

    location_pulled = False

    get_category = request.GET.get("que_categories", None)
    # get_plat = request.GET.get("que_platforms", None)
    loclong = request.GET.get("loclong", None)
    loclat = request.GET.get("loclat", None)

    featured_rentals = RentalGame.objects.filter(featured=True).all()
    the_featured_banner = RentalGame.objects.filter(featured_banner=True).last()

    trailers = RentalGameTrailer.objects.all().order_by("created_at")[:4]

    all_games = RentalGame.objects.none()

    if loclat is not None and loclong is not None:

        dest = (loclat, loclong)
        all_rental_games = RentalGame.objects.all().order_by("-created_at")
        range_items_id = [
            o.id for o in all_rental_games if o.checkInRadius(dest) == True
        ]
        print(range_items_id)
        all_games = all_rental_games.filter(id__in=range_items_id)
        location_pulled = True

    showing_cat = "All categories"

    if get_category is not None:

        if get_category != "all":
            the_cat = RentalCat.objects.get(name=get_category)
            all_games = all_games.filter(cat=the_cat).all().order_by("-created_at")
            showing_cat = the_cat.name

    page = request.GET.get("page", 1)

    paginator = Paginator(all_games, 15)

    try:
        all_games = paginator.page(page)
    except PageNotAnInteger:
        all_games = paginator.page(1)
    except EmptyPage:
        all_games = paginator.page(paginator.num_pages)

    cats = RentalCat.objects.all()

    context = {
        "featured_rentals": featured_rentals,
        "all_items": all_games,
        "the_featured_banner": the_featured_banner,
        "trailers": trailers,
        "cats": cats,
        "showing_cat": showing_cat,
        "location_pulled": location_pulled,
    }

    return render(request, template, context)


@login_required
def update_que(request):
    data = json.loads(request.body)
    productId = data["productId"]
    action = data["action"]
    number_of_days = data["no_of_days"]
    # from_date_data = data["from_date"]
    # to_date_data = data["to_date"]

    if request.user.is_authenticated and request.user.profile.profile_set_up == False:
        return redirect("users:user-profile")

    customer = request.user.profile
    product = RentalGame.objects.get(id=productId)
    # from_date = None
    # to_date = None

    # if from_date_data and to_date_data:
    #     from_date = datetime.strptime(from_date_data, "%Y-%m-%d").date()
    #     to_date = datetime.strptime(to_date_data, "%Y-%m-%d").date()

    if action == "add":

        # que_item, created = RentalQueItems.objects.get_or_create(
        #     item=product,
        #     user=customer,
        #     ordered=False,
        # )

        que_item_qs = RentalQueItems.objects.filter(
            item=product,
            user=customer,
            ordered=False,
        )
        if not que_item_qs.exists():
            que_item = RentalQueItems.objects.create(
                item=product,
                user=customer,
                ordered=False,
            )
        else:
            que_item = que_item_qs.last()

        if number_of_days:
            que_item.no_of_days = int(number_of_days)
            que_item.save()

        que_qs = RentalQue.objects.filter(user=customer, ordered=False)
        if que_qs.exists():
            que = que_qs[0]
            if que.items.filter(item=product).exists():
                que_item.quantity += 1
                que_item.save()
                print("This item quantity was updated")
            else:
                que.items.add(que_item)
                print("This item was added to your que")
        else:
            ordered_date = timezone.now()
            que = RentalQue.objects.create(user=customer, ordered_date=ordered_date)
            que.items.add(que_item)
            print("This item was added to your Q")

    elif action == "remove":
        que_qs = RentalQue.objects.filter(user=customer, ordered=False)
        if que_qs.exists():
            que = que_qs[0]
            # check if the order item is in the order
            if que.items.filter(item=product).exists():
                que_item = RentalQueItems.objects.filter(
                    item=product, user=customer, ordered=False
                )[0]
                que.items.remove(que_item)
                que_item.delete()
                print("This item was removed from your Q")
            else:
                print("This item was not  in ur Q")
        else:
            print("you do not have an active Q order")
    elif action == "remove-single":
        que_qs = RentalQue.objects.filter(user=customer, ordered=False)
        if que_qs.exists():
            que = que_qs[0]
            # check if the order item is in the order
            if que.items.filter(item=product).exists():
                que_item = RentalQueItems.objects.filter(
                    item=product, user=customer, ordered=False
                )[0]
                if que_item.quantity > 1:
                    que_item.quantity -= 1
                    que_item.save()
                else:
                    que.items.remove(que_item)
                print("The item was updated")
            else:
                print("This item was not in the Q")

        else:
            print("You do not have an active Q order")

    return JsonResponse("Item has been added to Que", safe=False)


@login_required
def the_que(request):
    data = queData(request)
    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    print(items)

    context = {"items": items, "que": order}

    return render(request, "rentals/the_que.html", context)


@login_required
def checkout(request):
    template = "rentals/checkout.html"
    data = queData(request)

    cartItems = data["cartItems"]
    order = data["order"]
    items = data["items"]

    if cartItems < 1:
        print("You don not have any item in your Q")
        return redirect("rentals:rental-home")

    context = {
        "items": items,
        "que": order,
        "address_regions": settings.ADDRESS_REGIONS,
    }

    return render(request, template, context)


@login_required
def process_checkout(request):
    data = json.loads(request.body)
    the_profile = request.user.profile

    billing_address = data["billingInfo"]["billing_address"]
    billing_city = data["billingInfo"]["billing_city"]
    billing_state = data["billingInfo"]["billing_state"]

    return_option = data["returnInfo"]["return_option"]
    pickup_option = data["shippingInfo"]["pickup_option"]

    try:
        que = RentalQue.objects.filter(
            user=the_profile, ordered=False, items__isnull=False
        ).last()
        try:
            que.shipping_fee = 0
            que.return_fee = 0
            que.save()
        except:
            pass
        if not que.billing_address:
            billing_address = Address.objects.create(
                user=the_profile,
                street_address=billing_address,
                city=billing_city,
                state=billing_state,
                address_type="B",
            )
            que.billing_address = billing_address

        if pickup_option == "no_pickup":
            shipping_address = data["shippingInfo"]["shipping_address"]
            shipping_city = data["shippingInfo"]["shipping_city"]

            new_shipping_address = Address.objects.create(
                user=the_profile,
                street_address=shipping_address,
                city=shipping_city,
                state="Lagos State",
                address_type="S",
            )

            que.shipping_address = new_shipping_address
            que.shipping_fee = 1500

        else:
            que.pick_up_prompt = True

        if return_option == "return":
            return_address = data["returnInfo"]["return_address"]
            return_city = data["returnInfo"]["return_city"]

            new_return_address = Address.objects.create(
                user=the_profile,
                street_address=return_address,
                city=return_city,
                state="Lagos State",
                address_type="R",
            )

            que.return_address = new_return_address
            que.return_fee = 1500
            que.return_prompt = True

        else:
            pass

        que.save()

    except ObjectDoesNotExist:
        print("You don not have any item in the Q")
        return redirect("rentals:rental-home")

    return JsonResponse(
        data={"the_profile_id": the_profile.pk, "the_que_id": que.pk},
    )


class PaymentView(View):
    def get(self, request, the_profile_id, que_id):
        template = "rentals/payment.html"

        the_profile = Profile.objects.get(pk=the_profile_id)

        que = RentalQue.objects.get(pk=que_id, ordered=False)
        if que.billing_address:

            host = self.request.get_host()

            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": "%.2f" % Decimal(que.get_total()).quantize(Decimal(".01")),
                "item_name": "Order {}".format(que.id),
                "invoice": str(que.id),
                "currency_code": "USD",
                "notify_url": "http://{}{}".format(host, reverse("paypal-ipn")),
                "return_url": "http://{}{}".format(
                    host, reverse("rentals:paypal_payment_done")
                ),
                "cancel_return": "http://{}{}".format(
                    host, reverse("rentals:paypal_payment_canceled")
                ),
            }

            paypal_form = PayPalPaymentsForm(initial=paypal_dict)

            context = {
                "que": que,
                "the_profile": the_profile,
                "paypal_form": paypal_form,
                "TEST_PAYSTACK_PUBLIC_KEY": settings.TEST_PAYSTACK_PUBLIC_KEY,
                "LIVE_PAYSTACK_PUBLIC_KEY": settings.LIVE_PAYSTACK_PUBLIC_KEY,
            }

            return render(self.request, template, context)

        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("rentals:checkout")

    def post(self, request, the_profile_id, que_id, *args, **kwargs):

        reference = self.request.POST.get("paystackToken")
        pay_method = self.request.POST.get("payment_type")
        # order = Order.objects.get(user=self.request.user.profile, ordered=False)
        que = RentalQue.objects.get(pk=que_id, ordered=False)
        the_profile = Profile.objects.get(pk=the_profile_id)

        # if pay_method == 'paystack':

        headers = {"Authorization": f"Bearer {settings.LIVE_PAYSTACK_SECRET_KEY}"}
        resp = requests.get(
            f"https://api.paystack.co/transaction/verify/{reference}", headers=headers
        )
        response = resp.json()

        try:
            status = response["data"]["status"]
            auth_code = response["data"]["authorization"]["authorization_code"]
            if status == "success":
                payment = RentalPayment()
                payment.txn_code = reference
                payment.amount = int(que.get_total())
                payment.user = the_profile
                payment.save()

                que_items = que.items.all()
                # order_items.update(ordered=True)
                que_item_total = 0
                for item in que_items:
                    item.ordered = True
                    item.save()
                    que_item_total += item.get_final_price()

                que.ordered = True
                que.payment = payment
                que.ref_code = create_ref_code()
                que.save()

                # send a successful card payment with receipt

                try:
                    subject, from_email, to = (
                        "YOUR ORDER IS ON THE WAY",
                        "GameOn <noreply@gameon.com.ng>",
                        [que.user.user.email],
                        # ["shola.albert@gmail.com"],
                    )

                    html_content = render_to_string(
                        "events/rental_order_successfull.html",
                        {
                            "que_items": que_items,
                            "que_item_total": que_item_total,
                            "que": que,
                        },
                    )
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()

                except Exception as e:
                    print("error", e)
                    pass

                # send a mail to admin too

                try:
                    subject, from_email, to = (
                        "NEW RENTAL ORDER MADE ",
                        "GameOn <noreply@gameon.com.ng>",
                        ["admin@gameon.com.ng"],
                        # ["shola.albert@gmail.com"],
                    )

                    html_content = render_to_string(
                        "events/admin_new_rental_order.html",
                        {
                            "que_items": que_items,
                            "que_item_total": que_item_total,
                            "que": que,
                            "email": que.user.user.email,
                        },
                    )
                    msg = EmailMessage(subject, html_content, from_email, to)
                    msg.content_subtype = "html"
                    msg.send()

                except:
                    pass

                messages.success(self.request, "Payment is successful")
                return redirect("rentals:rental-home")
            else:
                messages.warning(self.request, "Payment failed")
                return HttpResponseRedirect(reverse("rentals:payment"))

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
    return render(request, "rentals/paypal_payment_done.html")


@csrf_exempt
def paypal_payment_canceled(request):
    return render(request, "rentals/paypal_payment_canceled.html")


def about_us(request):
    template = "rentals/about_us.html"
    context = {"page_title": "About Us"}
    return render(request, template, context)


def privacy_policy(request):
    template = "rentals/privacy_policy.html"
    context = {"page_title": "Privacy & Policy"}
    return render(request, template, context)


def t_and_c(request):
    template = "rentals/t_and_c.html"
    context = {"page_title": "Terms & Conditions"}
    return render(request, template, context)


def RentalGameDetails(request, item_id):
    template = "rentals/rental_game_details.html"
    item = RentalGame.objects.get(id=item_id)
    dest = (item.vendor_lat, item.vendor_long)
    all_other_items_qs = RentalGame.objects.exclude(id=item_id)
    range_items_id = [o.id for o in all_other_items_qs if o.checkInRadius(dest) == True]
    all_items = RentalGame.objects.filter(id__in=range_items_id)
    context = {"item": item, "all_items": all_items}
    return render(request, template, context)


def not_available(request):
    template = "rentals/not_available.html"
    context = {"page_title": "Not Available"}
    return render(request, template, context)
