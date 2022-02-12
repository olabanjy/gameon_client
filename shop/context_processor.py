from .models import *

from .utils import *


def getCartCount(request):
    data = cartData(request)
    cartItems = data["cartItems"]
    return {"count": cartItems}


def getCartTotal(request):
    data = cartData(request)
    order = data["order"]
    return {"cartTotal": order}


# def brandlist(request):
#     brands = Brand.objects.all()
#     return {"brands": brands}


# def cartitemcount(request):
#     if request.user.is_authenticated:
#         itemcount = OrderItem.objects.filter(order__order_status=False).filter(
#             order__customer=request.user
#         )

#         return {"itemcount": itemcount}
#     else:
#         return {"itemcount": OrderItem.objects.none()}


# def general_info(request):
#     info = GeneralInfo.objects.first()
#     return {"info": info}


# def order_returns(request, username):
#     pass


# def multiply(qty, unit_price, *args, **kwargs):
#     return qty * unit_price
