from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseForbidden,
    HttpResponseServerError,
    JsonResponse,
)
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse, reverse_lazy
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.template.loader import render_to_string
from allauth.account.views import PasswordChangeView, _ajax_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta, date, datetime, time
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from allauth.account.admin import EmailAddress
from allauth.account.utils import send_email_confirmation
from twilio.rest import Client as TwilioClient

from shop.models import *
from rentals.models import *

from .models import *
from .utils import *
from .tasks import *
import pyotp
import random, string, time, re, requests


class UserProfile(View):
    def get(self, request, *args, **kwargs):

        template = "users/user_profile.html"

        profile = self.request.user.profile

        order_items = OrderItem.objects.filter(user=profile, ordered=True).all()
        que_items = RentalQueItems.objects.filter(user=profile, ordered=True).all()

        orders = Order.objects.filter(user=profile, ordered=True).all()[:10]
        ques = RentalQue.objects.filter(user=profile, ordered=True).all()[:10]

        print(self.request.user.profile.kyc_status)
        print(self.request.user.profile.address_verification_status)
        user_add = None
        def_add = Address.objects.filter(
            user=self.request.user.profile, address_type="P"
        )
        if def_add.exists():
            user_add = def_add.first()

        context = {
            "page_title": "My Account",
            "profile": profile,
            "order_items": order_items,
            "orders": orders,
            "user_add": user_add,
            "que_items": que_items,
            "ques": ques,
        }

        return render(self.request, template, context)


@login_required
def update_profile(request):
    data = {}
    first_name = request.POST.get("first_name", None)
    last_name = request.POST.get("last_name", None)
    phone = request.POST.get("phone", None)
    print(request.POST.get("csrfmiddlewaretoken", None))
    print(first_name)
    print(last_name)
    print(phone)
    profile = request.user.profile
    try:
        profile.first_name = first_name
        profile.last_name = last_name
        profile.phone = phone
        profile.profile_set_up = True
        profile.save()
        print(
            f"updated profile are {profile.first_name}, {profile.last_name} and {profile.phone} "
        )
        if profile.welcome_email == "pending":
            try:
                subject, from_email, to = (
                    "WELCOME TO GAMEON",
                    "GameOn <noreply@gameon.com.ng>",
                    [request.user.email],
                )

                html_content = render_to_string(
                    "events/welcome_email.html",
                    {
                        "first_name": profile.first_name,
                        "last_name": profile.last_name,
                    },
                )
                msg = EmailMessage(subject, html_content, from_email, to)
                msg.content_subtype = "html"
                msg.send()

                profile.welcome_email = "sent"
                profile.save()
            except:
                pass
        else:
            pass

        data.update({"status": True, "msg": "Profile Updated"})

    except:
        print("Error occured!")
        data.update({"status": False, "msg": "Error Occured!"})

    return JsonResponse(data)


@login_required
def update_address(request):
    data = {}
    street_address = request.POST.get("street_address", None)
    apartment_address = request.POST.get("apartment_address", None)
    city = request.POST.get("city", None)
    state = request.POST.get("state", None)
    print(request.POST.get("csrfmiddlewaretoken", None))
    print(street_address)
    print(apartment_address)
    print(city)
    profile = request.user.profile
    try:
        user_address = Address.objects.filter(user=profile, address_type="P")
        if user_address.exists():
            the_add = user_address.first()
            the_add.street_address = street_address
            the_add.city = city
            the_add.state = state
            the_add.apartment_address = apartment_address
            the_add.save()
        else:
            user_address = Address.objects.create(
                user=profile,
                street_address=street_address,
                city=city,
                state=state,
                apartment_address=apartment_address,
                address_type="P",
            )

        print(f"updated address of {profile.first_name}, {profile.last_name}")
        data.update({"status": True, "msg": "Address Updated"})
    except:
        print("Error occured!")
        data.update({"status": False, "msg": "Error Occured!"})

    return JsonResponse(data)


@login_required
def update_identity(request):
    data = {}
    if request.method == "POST":
        print("its a post request")
        if "id_verification" in request.FILES:
            id_file = request.FILES["id_verification"]
            print(id_file)
            profile = request.user.profile
            try:
                user_kyc, created = UserKYC.objects.get_or_create(user=profile)
                user_kyc.photo = id_file
                user_kyc.status = "submitted"
                user_kyc.save()
                print(f"updated kyc of {profile.first_name}, {profile.last_name}")
                data.update({"status": True, "msg": "Identity Document Updated"})
            except:
                print("Error occured!")
                data.update({"status": False, "msg": "Error Occured!"})
    return JsonResponse(data)


@login_required
def update_profile_photo(request):
    data = {}
    if request.method == "POST":
        print("its a post request")
        # update_profile_photo_input
        if "update_profile_photo_input" in request.FILES:
            photo_file = request.FILES["update_profile_photo_input"]
            print(photo_file)
            profile = request.user.profile
            try:
                profile.photo = photo_file
                profile.save()
                data.update({"status": True, "msg": "Profile Photo Updated"})
            except:
                print("Error occured!")
                data.update({"status": False, "msg": "Error Occured!"})

    return JsonResponse(data)

    pass


@login_required
def update_address_verification(request):
    data = {}
    if request.method == "POST":
        print("its a post request")
        if "address_verification" in request.FILES:
            address_file = request.FILES["address_verification"]
            print(address_file)
            profile = request.user.profile
            try:
                user_add, created = AddressVerification.objects.get_or_create(
                    user=profile
                )
                user_add.photo = address_file
                user_add.status = "submitted"
                user_add.save()
                print(f"updated kyc of {profile.first_name}, {profile.last_name}")
                data.update({"status": True, "msg": "Address Document Updated"})
            except:
                print("Error occured!")
                data.update({"status": False, "msg": "Error Occured!"})

    return JsonResponse(data)
