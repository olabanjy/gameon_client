from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from rentals.views import error404, error500
from django.contrib.auth.decorators import login_required

from django.conf.urls import handler404, handler500


urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("rentals.urls", namespace="rentals")),
    path("shop/", include("shop.urls", namespace="shop")),
    path("u/", include("users.urls", namespace="users")),
    path("paypal/", include("paypal.standard.ipn.urls")),
]


urlpatterns += [
    path("api/v1/", include("gameon.api_router")),
]


handler404 = error404
handler500 = error500


if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path("__debug__/", include(debug_toolbar.urls))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = error404
handler500 = error500
