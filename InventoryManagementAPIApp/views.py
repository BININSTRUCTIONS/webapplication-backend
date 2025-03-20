from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


from .models import *


# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def register_business(request):
    response = {"status": "failed"}
    data = request.data
    business_name = data["businessName"]
    business_type = data["businessType"]

    business_type = BusinessType.objects.get(id=business_type)
    if business_type is not None:
        business = Business.objects.create(name=business_name, user=request.user, type=business_type)
        if business is not None:
            response["status"] = "ok"
        else:
            response["message"] = "couldn't register the business. please try again later"
    else:
        response["message"] = "Not a valid business type"
    return Response(response)


@api_view(["GET"])
@permission_classes([])
@authentication_classes([])
def get_business_types(request):
    response = {"status": "failed"}
    business_types = []
    for item in BusinessType.objects.all():
        business_types.append({
            "id": item.id,
            "type": item.type
        })
    response["types"] = business_types
    response["status"] = "ok"
    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_business(request):
    response = {"status": "failed"}
    business_list = []
    for business in Business.objects.filter(user=request.user):
        business_list.append({
            "id": business.id,
            "name": business.name,
            "type": business.type.type
        })
    response["status"] = "ok"
    response["businessList"] = business_list
    return Response(response)