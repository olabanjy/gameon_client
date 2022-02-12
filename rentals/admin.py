from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(RentalPlatform)
admin.site.register(RentalGameTrailer)
admin.site.register(RentalCat)
admin.site.register(RentalGame)
admin.site.register(RentalQueItems)
admin.site.register(RentalQue)
admin.site.register(RentalPayment)
admin.site.register(RentalRefund)
admin.site.register(RentalWebhookBackup)
