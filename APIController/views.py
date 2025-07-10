from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

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
    IsAdminUser
)

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


from api.models import Customer
from KeyManager.models import DigitalKey
from ProductApp.models import CompanyProduct

from APIs.models import APIKey
from api.models import CustomersHavePlans

from .utils.decorators import key_manager_api_authentication


import random
import string


# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def generate_key_manager_api_key(request):
    response = {"status": "failed"}
    key = ''.join(random.choices(string.ascii_letters + string.digits, k=200))
    try:
        user = request.user
        customer = Customer.objects.get(user=user)
        product = CompanyProduct.objects.get(id=1)

        customer_has_plan = CustomersHavePlans.objects.get(customer=customer, product=product)

        if customer_has_plan:
            api_key = APIKey.objects.create(
                api_key=key,
                customers_have_plans=customer_has_plan
            )

        if api_key is not None:
            response["key"] = key
            response["status"] = "ok"
    except Exception as e:
        print("Error generating an API Key")
        print(e)

    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_api_keys(request):
    response = {"status": "failed"}

    try:
        customer = Customer.objects.get(user=request.user)
        product = CompanyProduct.objects.get(id=1)
        customers_have_plans = CustomersHavePlans.objects.get(customer=customer, product=product)

        if customers_have_plans:
            api_keys = APIKey.objects.filter(customers_have_plans=customers_have_plans)

            keys_information = []
            for key in api_keys:
                keys_information.append({
                    "id": key.id,
                    "key": key.api_key,
                    "last_used": key.last_used,
                    "remaining_requests": key.remaining_requests,
                    "requests_made": key.requests_made,
                })
            response["keysInformation"] = keys_information
            response["status"] = "ok"
    except Exception as e:
        pass
    # print(response)
    return Response(response)
