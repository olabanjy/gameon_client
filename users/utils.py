from django.conf import settings
import pyotp
import requests
import datetime
import pytz


def time_of_day():
    cur_time = datetime.datetime.now(tz=pytz.timezone(str(settings.TIME_ZONE)))
    if cur_time.hour < 6:
        return "Dawn"
    elif 6 <= cur_time.hour < 12:
        return "Morning"
    elif 12 <= cur_time.hour < 16:
        return "Afternoon"
    elif 16 <= cur_time.hour < 19:
        return "Evening"
    else:
        return "Night"
