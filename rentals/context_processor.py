from .models import *

from .utils import *


def getQueCount(request):
    data = queData(request)
    cartItems = data["cartItems"]
    return {"queCount": cartItems}


def getQueTotal(request):
    data = queData(request)
    order = data["order"]
    return {"queTotal": order}
