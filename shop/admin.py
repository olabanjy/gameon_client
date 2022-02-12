from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(ItemPlatform)
admin.site.register(ItemCat)
admin.site.register(ItemType)
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
