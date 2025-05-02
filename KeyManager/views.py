from django.shortcuts import render
from django.http import FileResponse, JsonResponse
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

from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import *

import datetime
import hashlib

from django.conf import settings
from ProductApp.models import *
from api.models import Customer, CustomersHavePlans



# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_key_manager_keys(request):
    response = {"status": "failed"}
    keys = []
    for digital_key in DigitalKey.objects.all():
        keys.append({
            "id": digital_key.id,
            "key": digital_key.key,
            "max_activations": digital_key.max_activations,
            "current_activations": digital_key.current_activations,
            "is_active": digital_key.is_active
        })

    response["status"] = "ok"
    response["keys"] = keys
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def add_key_manager_key(request):
    response = {"status": "failed"}
    message = ""
    data = request.data
    try:
        # print(data)
        max_activations = data["maxActivations"]
        is_available = data["isActivated"]

        user = request.user
        username = user.username

        customer = Customer.objects.get(user=user)
        print(customer)
        print(dir(customer))
        product = CompanyProduct.objects.get(id=1)
        plan = customer.customershaveplans_set.filter(product=product, customer=customer)
        print(product)
        print(plan)

        generate_key = False
        keys = DigitalKey.objects.filter(user=user)
        if plan[0].id == 1:
            if len(keys) < 5:
                generate_key = True
            else:
                message = "You have generated maximum number of keys allowed. Upgrade your plan."
        elif len(plan) == 0:
            message = "you haven't subscribed to any plan. subscribe to the plan you want before generating any key"
        else:
            generate_key = True
            
        if generate_key:
            # print(customer.customer_has_plan)

            hash_string = f"{username}-{datetime.datetime.now()}-"
            hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
            hash = f"bininstructions-km-{hash}"

            digital_key = DigitalKey.objects.create(
                key=hash,
                max_activations=max_activations,
                current_activations=0,
                is_active=is_available,
                user=user
            )
            if digital_key is not None:
                response["status"] = "ok"
        else:
            response["message"] = message
    except Exception as exception:
        print(exception)
        pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def change_key_manager_key(request):
    response = {"status": "failed"}
    data = request.data
    try:
        # print(data)

        id = data["id"]
        max_activations = data["max_activations"]
        current_activations = data["current_activations"]
        is_active = data["is_active"]

        digital_key = DigitalKey.objects.get(id=id)
        if digital_key is not None:
            digital_key.max_activations = max_activations
            digital_key.current_activations = current_activations
            digital_key.is_active = is_active
            digital_key.save()
            response["status"] = "ok"
    except Exception as exception:
        # print(exception)
        pass
    return Response(response)



@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_key_data(request):
    response = {"status": "failed", "keyData": ""}
    data = request.data
    try:
        # print(data)
        digital_key = None
        try:
            id = data["id"]
            digital_key = DigitalKey.objects.get(id=id)
        except:
            key = data["key"]
            digital_key = DigitalKey.objects.get(key=key)

        if digital_key is not None:
            data = {
                "id": digital_key.id,
                "key": digital_key.key,
                "max_activations": digital_key.max_activations,
                "current_activations": digital_key.current_activations,
                "is_active": digital_key.is_active
            }
            response["keyData"] = data
    except Exception as exception:
        # print(exception)
        pass
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_plan(request):
    response = {"status": "failed"}
    data = request.data
    try:
        product_id = data["productID"]
        plan_id = data["planID"]

        company_product = CompanyProduct.objects.get(id=product_id)
        if company_product is not None:
            try:
                plan = company_product.subscriptionplan_set.get(id=plan_id)
                print(plan)

                payment_data = {}

                recurring_period = "Month"
                if plan.term == "y":
                    recurring_period = "Year"

                try:
                    customer = Customer.objects.get(user=request.user)
                    
                    customer_has_plan = CustomersHavePlans.objects.create(
                        customer=customer,
                        plans=plan,
                        date=datetime.datetime.now()
                    )
                except:
                    pass

                payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
                payment_data["return_url"] = None
                payment_data["cancel_url"] = None
                payment_data["notify_url"] = "http://sample.com/notify"
                payment_data["first_name"] = request.user.first_name
                payment_data["last_name"] = request.user.last_name
                payment_data["email"] = request.user.email
                payment_data["phone"] = None
                payment_data["address"] = None
                payment_data["city"] = None
                payment_data["country"] = None
                payment_data["order_id"] = f"{company_product.id}-{plan.id}"
                payment_data["items"] = company_product.name + " " + plan.name
                payment_data["currency"] = "USD"
                payment_data["recurrence"] = f"1 {recurring_period}"
                payment_data["duration"] = "Forever"
                payment_data["amount"] = plan.price

                hash_string = settings.PAYHERE_MERCHANT_ID + f"{company_product.id}-{plan.id}" + ("%.2f" % plan.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
                hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
                payment_data["hash"] = hash
                response["paymentData"] = payment_data
                response["status"] = "ok"
                # print(dir(company_product))
            except Exception as e_:
                # print(e_)
                pass

    except Exception as e:
        # print(e)
        pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_key_manager_data(request):
    response = {"status": "failed"}
    user = request.user
    # print(dir(user))
    customer = user.customer
    # print(dir(customer))
    if customer is not None:
        plans = customer.subscription_plans.filter(product=2) # 2 is the id of the KeyManager product
        # print(dir(plans))
        print(plans)
        if len(plans) == 1:
            response["planActivated"] = True
            response["status"] = "ok"
    return Response(response)
