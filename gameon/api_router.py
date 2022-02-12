from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter


from rentals.api.views import (
    RentalPlatformViewSet,
    RentalCatViewSet,
    RentalGamesViewSet,
)

from shop.api.views import ItemPlatformViewSet, ItemCatViewSet, ItemTypeViewSet

from users.api.views import ProfileViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("rental/platform", RentalPlatformViewSet)
router.register("rental/cat", RentalCatViewSet)
router.register("rental/items", RentalGamesViewSet)
router.register("shop/item/platform", ItemPlatformViewSet)
router.register("shop/item/cat", ItemCatViewSet)
router.register("shop/item/type", ItemTypeViewSet)


router.register("users", ProfileViewSet)


app_name = "api"
urlpatterns = router.urls
