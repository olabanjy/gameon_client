from django.contrib.auth import get_user_model
from django.http import HttpResponse
from rest_framework import status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser

from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers
from django.shortcuts import reverse
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response

from uuid import uuid4
from django.utils import datetime_safe

from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .serializers import *


User = get_user_model()


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    @action(detail=False, methods=["GET"])
    def get_all_users(self, request):
        all_profiles = Profile.objects.all()
        serializer = self.get_serializer(all_profiles, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    @action(detail=False, methods=["POST"])
    def approve_kyc(self, request):
        try:
            kyc_id = request.data["kyc_id"]
            the_kyc = UserKYC.objects.get(id=kyc_id)
            the_kyc.verified = True
            the_kyc.status = "approved"

            the_kyc.save()

            return Response({"message": "KYC Approved"}, status=status.HTTP_200_OK)

        except UserKYC.DoesNotExist:
            return Response(
                {"message": "KYC object not found"}, status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["POST"])
    def approve_ad(self, request):
        try:
            ad_id = request.data["ad_id"]
            the_ad = AddressVerification.objects.get(id=ad_id)
            the_ad.verified = True
            the_ad.status = "approved"

            the_ad.save()

            return Response({"message": "Address Approved"}, status=status.HTTP_200_OK)

        except UserKYC.DoesNotExist:
            return Response(
                {"message": "Address object not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )
