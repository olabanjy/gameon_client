from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "shop"

urlpatterns = [
    path("", shopHome, name="shop-home"),
    path("search_item/", search_result, name="search_item"),
    path("details/<item_id>/", itemDetail, name="details"),
    path("cart/", cart, name="shop-cart"),
    path("update-item/", update_item, name="update-item"),
    path("checkout/", checkout, name="shop-checkout"),
    path("process_checkout/", process_checkout, name="process_checkout"),
    path(
        "payment/<int:the_profile_id>/<int:the_order_id>/",
        PaymentView.as_view(),
        name="shop-payment",
    ),
    # Paypal
    path("payment-done/", paypal_payment_done, name="paypal_payment_done"),
    path("payment-cancelled/", paypal_payment_canceled, name="paypal_payment_canceled"),
    # Paystack
    path(
        "paystack_webhook/",
        paystack_test_webhook_view,
        name="paystack_test_webhook_view",
    ),
]
