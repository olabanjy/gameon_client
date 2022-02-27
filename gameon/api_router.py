from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter


from rentals.api.views import (
    RentalPlatformViewSet,
    RentalCatViewSet,
    RentalGamesViewSet,
    RentalQueViewSet,
    TrailersViewSet,
)

from shop.api.views import (
    ItemPlatformViewSet,
    ItemCatViewSet,
    ItemTypeViewSet,
    ItemsViewSet,
    OrderViewSet,
)

from users.api.views import ProfileViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("rental/platform", RentalPlatformViewSet)
router.register("rental/cat", RentalCatViewSet)
router.register("rental/items", RentalGamesViewSet)
router.register("rental/que", RentalQueViewSet)


router.register("shop/item/platform", ItemPlatformViewSet)
router.register("shop/item/cat", ItemCatViewSet)
router.register("shop/item/type", ItemTypeViewSet)
router.register("shop/items", ItemsViewSet)
router.register("shop/items", ItemsViewSet)
router.register("shop/item/order", OrderViewSet)


router.register("trailers", TrailersViewSet)


router.register("users", ProfileViewSet)


app_name = "api"
urlpatterns = router.urls
