from django.urls import path, include
from .views import *
from django.contrib.auth.decorators import login_required

app_name = "users"

urlpatterns = [
    path(
        "account/settings/", login_required(UserProfile.as_view()), name="user-profile"
    ),
    path("update-profile/", update_profile, name="update-profile"),
    path("update-address/", update_address, name="update-address"),
    path("update-identity/", update_identity, name="update-identity"),
    path("update-profile-photo/", update_profile_photo, name="update-profile-photo"),
    path(
        "update-address-verification/",
        update_address_verification,
        name="update-address-verification",
    ),
    path("fetchUserObject/", fetchUserObject, name="fetchUserObject"),
]
