from __future__ import absolute_import, unicode_literals
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives, send_mail, EmailMessage
from django.template.loader import render_to_string
import time, pytz
from datetime import timedelta, date, datetime
import requests
from celery import shared_task
import glob
import os
from .models import UserLoginActivity


@shared_task
def save_user_login_info(user_id, browser, device, os, city, country, location, ip):
    print(f"{user_id}, {browser}, {device}, {os}, {city}, {country}, {location}, {ip}")
    # try:
    login_user = User.objects.get(pk=user_id)
    new_login = UserLoginActivity.objects.create(
        user=login_user,
        login_IP=ip,
        user_agent_info=f"{browser}/{device}/{os}",
        login_city=city,
        login_country=country,
        login_loc=location,
    )
    print("new login info saved")
    # except:
    #     print("Error saving login info")


@shared_task
def send_login_notification(user_id, browser, device, os, city, country, location, ip):
    user = User.objects.get(pk=user_id)
    try:
        today = datetime.now()
        time_now = pytz.utc.localize(today)
        subject, from_email, to = (
            "Login Notification",
            "Support <noreply@gameon.com.ng>",
            [user.email],
        )

        html_content = render_to_string(
            "events/login_notification.html",
            {
                "username": user.username,
                "browser": browser,
                "device": device,
                "os": os,
                "time_now": time_now,
            },
        )
        msg = EmailMessage(subject, html_content, from_email, to)
        msg.content_subtype = "html"
        msg.send()

    except (ValueError, NameError, TypeError) as error:
        err_msg = str(error)
        print(err_msg)
    except:
        print("Unexpected Error")
