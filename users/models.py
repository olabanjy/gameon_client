from django.db import models
from django.conf import settings
from django.urls import reverse
from django.db.models.signals import post_save, post_init, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.db.models import Sum
from allauth.account.signals import user_signed_up, user_logged_in
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django_countries.fields import CountryField
from datetime import timedelta, date, datetime
from PIL import Image
import uuid
import random, string
import pyotp


DEV_PHASE = (("live_prod", "Live Prod"), ("staging", "Staging"), ("beta", "Beta"))


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_code = models.CharField(max_length=200)
    key = models.CharField(max_length=100, unique=True, blank=True)
    enable_2fa = models.BooleanField(default=False)
    phone = models.CharField(max_length=40, null=True, blank=True)
    phone_verified = models.BooleanField(default=False)
    first_name = models.CharField(blank=True, null=True, max_length=200)
    last_name = models.CharField(blank=True, null=True, max_length=200)
    dob = models.DateField(max_length=100, blank=True, null=True)
    gender = models.CharField(max_length=200, blank=True, null=True)
    welcome_email = models.CharField(max_length=100, default="pending")
    profile_set_up = models.BooleanField(default=False)
    dev_phase = models.CharField(max_length=200, choices=DEV_PHASE, default="beta")
    photo = models.ImageField(
        upload_to="gameon/user_profile/", default="default_profile_pics.jpg", blank=True
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.email

    @property
    def last_login(self, *args, **kwargs):
        the_last_login = self.user.last_login
        if the_last_login:
            user_last_login = the_last_login.strftime("%Y-%m-%d %H:%M")
            return user_last_login
        return None

    @property
    def kyc_status(self, *args, **kwargs):
        user_kyc = self.user_kyc
        if user_kyc.exists():
            return user_kyc.first().status
        return None

    @property
    def address_verification_status(self, *args, **kwargs):
        user_ad_verification = self.user_address_verification
        if user_ad_verification.exists():
            return user_ad_verification.first().status
        return None

    def authenticate(self, otp):
        """This method authenticates the given otp"""
        provided_otp = 0
        try:
            provided_otp = int(otp)
        except:
            return False
        t = pyotp.TOTP(self.key, interval=900)

        return t.verify(provided_otp)


def profile_receiver(sender, instance, created, *args, **kwargs):

    if created:
        profile = Profile.objects.get_or_create(user=instance)

    profile, created = Profile.objects.get_or_create(user=instance)

    if profile.user_code is None or profile.user_code == "":
        profile.user_code = str(
            "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        )
        profile.save()


post_save.connect(profile_receiver, sender=settings.AUTH_USER_MODEL)


class AvailableCountry(models.Model):
    unique_code = models.CharField(max_length=200)
    country = CountryField(blank=True, null=True)

    def __str__(self):
        return self.country.name


LOGIN_STATUS = (
    ("success", "Success"),
    ("failed", "Failed"),
)


class UserLoginActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_IP = models.CharField(max_length=200, null=True, blank=True)
    login_datetime = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=100, default="success", choices=LOGIN_STATUS, null=True, blank=True
    )
    user_agent_info = models.CharField(max_length=255, blank=True, null=True)
    login_city = models.CharField(max_length=255, blank=True, null=True)
    login_country = models.CharField(max_length=255, blank=True, null=True)
    login_loc = models.CharField(max_length=255, blank=True, null=True)
    login_other_info = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.email


ADDRESS_CHOICES = (
    ("B", "Billing"),
    ("S", "Shipping"),
    ("P", "Primary"),
)


class Address(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100, null=True)
    apartment_address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=300, blank=True, null=True)
    state = models.CharField(max_length=300, blank=True, null=True)
    country = CountryField(multiple=False, blank=True, null=True)
    zip = models.CharField(max_length=100, blank=True, null=True)
    address_type = models.CharField(
        max_length=1, choices=ADDRESS_CHOICES, null=True, blank=True
    )
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.user.email


VERIF_STATUS = (
    ("not_submitted", "Not Submitted"),
    ("submitted", "Submitted"),
    ("pending", "Pending"),
    ("rejected", "Rejected"),
    ("approved", "Approved"),
)


class UserKYC(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="user_kyc")
    id_type = models.CharField(max_length=200, null=True, blank=True)
    id_unique_number = models.CharField(null=True, max_length=200, blank=True)
    photo = models.FileField(
        upload_to="gameon/kyc/front_path/",
        default="default_photo.jpg",
    )
    photo_2 = models.FileField(
        upload_to="gameon/kyc/front_back/",
        default="default_photo.jpg",
    )
    status = models.CharField(
        max_length=100, default="not_submitted", choices=VERIF_STATUS
    )
    verified = models.BooleanField(default=False)
    verified_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.user.username

    class Meta:
        ordering = ("-created_at",)


class AddressVerification(models.Model):
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="user_address_verification"
    )
    id_type = models.CharField(max_length=200, null=True, blank=True)
    photo = models.FileField(
        upload_to="gameon/address_verification/",
        default="default_photo.jpg",
        blank=True,
    )
    status = models.CharField(
        max_length=100, default="not_submitted", choices=VERIF_STATUS, null=True
    )
    verified = models.BooleanField(default=False, blank=True)
    verified_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.user.username

    class Meta:
        ordering = ("-created_at",)
