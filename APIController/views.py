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
                    "key": key.api_key
                })
            response["keysInformation"] = keys_information
            response["status"] = "ok"
    except Exception as e:
        pass
    # print(response)
    return Response(response)



@csrf_exempt
@key_manager_api_authentication
def get_key_manager_key_information(request):
    response = {"status": "failed"}
    data = request.POST
    print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        response["keyInformation"] = {
            "id": digital_key.id,
            "maxActivations": digital_key.max_activations,
            "currentActivations": digital_key.current_activations,
            "isActive": digital_key.is_active,
        }
        response["status"] = "ok"
    except:
        response["message"] = "Invalid key provided"
    print("Called get key state function")
    return JsonResponse(response)


@csrf_exempt
@key_manager_api_authentication
def activate_key(request):
    response = {"status": "failed"}
    data = request.POST
    print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        if digital_key.current_activations < digital_key.max_activations:
            digital_key.current_activations = digital_key.current_activations + 1
            response["status"] = "ok"
        else:
            response["message"] = "Maximum activation count reached. cannot use this key for activating. deactivate one usage of the key or increase the number of activations for the key"
    except:
        response["message"] = "Invalid key provided"
    print("Called get key state function")
    return JsonResponse(response)


@csrf_exempt
@key_manager_api_authentication
def mark_key_as_active(request):
    response = {"status": "failed"}
    data = request.POST
    print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        digital_key.is_active = data["isActive"]
        digital_key.save()
        response["status"] = "ok"
    except:
        response["message"] = "Invalid key provided"
    print("Called get key state function")
    return JsonResponse(response)
