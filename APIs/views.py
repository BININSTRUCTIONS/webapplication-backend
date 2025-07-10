from django.shortcuts import render
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

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from ProductApp.models import CompanyProduct
from api.models import API, Customer


# Create your views here.
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_api(request):
    response = {"status": "failed"}
    data = request.data
    try:
        name = data["name"]
        product_id = data["productID"]

        try:
            product = CompanyProduct.objects.get(id=product_id)
            api = API.objects.create(name=name, product=product)
            if api is not None:
                response["status"] = "ok"
        except:
            pass
    except Exception as e:
        print(e)
        pass

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_api(request):
    response = {"status": "failed"}
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_api(request):
    response = {"status": "failed"}
    data = request.data
    try:
        api_id = data["apiID"]
    except:
        pass
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_apis(request):
    response = {"status": "failed"}
    products = CompanyProduct.objects.all()
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_subscribed_apis(request):
    response = {"status": "failed"}
    user = request.user
    try:
        customer = Customer.objects.get(user=user)
        subscribed_plans = customer.customershaveplans_set.all()
        data = []
        for plan in subscribed_plans:
            subscribed_plan = plan.plan
            product = subscribed_plan.product
            api_information = subscribed_plan.api_information

            if api_information is not None:
                information = {
                    "subscribedPlanID": plan.id,
                    "product": {
                        "name": product.name
                    },
                    "api_information": {
                        "name": f"{product.name} API",
                        "cpm": api_information.calls_per_minute
                    }
                }

            data.append(information)

        response["data"] = data
        response["status"] = "ok"
    except Exception as e:
        print(e)
    return Response(response)



