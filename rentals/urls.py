from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required
from .views import *

app_name = "rentals"

urlpatterns = [
    path("", rentalsHome, name="rental-home"),
    path("about-us/", about_us, name="about-us"),
    path("privacy-and-policy/", privacy_policy, name="privacy-and-policy"),
    path("terms-and-conditions/", t_and_c, name="terms-and-conditions"),
    path("update-que/", update_que, name="update_que"),
    path("que/", the_que, name="que"),
    path("checkout/", checkout, name="checkout"),
    path("process_checkout/", process_checkout, name="process_checkout"),
    path(
        "payment/<int:the_profile_id>/<int:que_id>/",
        login_required(PaymentView.as_view()),
        name="payment",
    ),
    path("payment-done/", paypal_payment_done, name="paypal_payment_done"),
    path("payment-cancelled/", paypal_payment_canceled, name="paypal_payment_canceled"),
]
