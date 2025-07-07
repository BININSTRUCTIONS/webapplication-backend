from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
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
from api.models import Customer, CustomersHavePlans, PaymentReceipt
from APIController.utils.decorators import key_manager_api_authentication

import json



# Create your views here.
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_key_manager_keys(request):
    response = {"status": "failed"}
    keys = []
    user = request.user
    for digital_key in DigitalKey.objects.filter(user=user):
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
        # print(customer)
        # print(dir(customer))
        product = CompanyProduct.objects.get(id=1)
        plan = customer.customershaveplans_set.filter(product=product, customer=customer)
        # print(product)
        # print(plan)

        generate_key = False
        keys = DigitalKey.objects.filter(user=user)
        if len(plan) > 0:
            # print("Plan ID: ", plan[0].plan.id)
            # print("Number of keys: ", len(keys))
            if plan[0].plan.id == 1:
                if len(keys) < 10:
                    generate_key = True
                else:
                    message = "You have generated maximum number of keys allowed. Upgrade your plan."
            elif plan[0].plan.id == 2:
                if len(keys) < 100:
                    generate_key = True
                else:
                    message = "You have generated maximum number of keys allowed. Upgrade your plan."
            elif plan[0].plan.id == 3:
                if len(keys) < 500:
                    generate_key = True
                else:
                    message = "You have generated maximum number of keys allowed. Upgrade your plan."
            elif plan[0].plan.id == 4:
                if len(keys) < 2000:
                    generate_key = True
                else:
                    message = "You have generated maximum number of keys allowed. Upgrade your plan."
            else:
                generate_key = True
        elif len(plan) == 0:
                message = "you haven't subscribed to any plan. subscribe to the plan you want before generating any key"
            
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



# This view is outdated
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_plan(request):
    response = {"status": "failed"}
    # data = request.data
    # try:
    #     product_id = data["productID"]
    #     plan_id = data["planID"]

    #     company_product = CompanyProduct.objects.get(id=product_id)
    #     if company_product is not None:
    #         try:
    #             plan = company_product.subscriptionplan_set.get(id=plan_id)
    #             print(plan)

    #             payment_data = {}

    #             recurring_period = "Month"
    #             if plan.term == "y":
    #                 recurring_period = "Year"

    #             try:
    #                 customer = Customer.objects.get(user=request.user)
                    
    #                 customer_has_plan = CustomersHavePlans.objects.create(
    #                     customer=customer,
    #                     plans=plan,
    #                     date=datetime.datetime.now()
    #                 )
    #             except Exception as e:
    #                 print(e)

    #             order_id = f"{company_product.id}-{plan.id}"

    #             payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
    #             payment_data["return_url"] = None
    #             payment_data["cancel_url"] = None
    #             payment_data["notify_url"] = "http://sample.com/notify"
    #             payment_data["first_name"] = request.user.first_name
    #             payment_data["last_name"] = request.user.last_name
    #             payment_data["email"] = request.user.email
    #             payment_data["phone"] = None
    #             payment_data["address"] = None
    #             payment_data["city"] = None
    #             payment_data["country"] = None
    #             payment_data["order_id"] = order_id
    #             payment_data["items"] = company_product.name + " " + plan.name
    #             payment_data["currency"] = "USD"
    #             payment_data["recurrence"] = f"1 {recurring_period}"
    #             payment_data["duration"] = "Forever"
    #             payment_data["amount"] = plan.price

    #             payment_receipt = PaymentReceipt.objects.create(
    #                 order_id=order_id,
    #                 first_name=request.user.first_name,
    #                 last_name=request.user.last_name,
    #                 email=request.user.email,
    #                 items=company_product.name + " " + plan.name,
    #                 currency="USD",
    #                 duration="Forever",
    #                 amount=plan.price
    #             )

    #             hash_string = settings.PAYHERE_MERCHANT_ID + f"{company_product.id}-{plan.id}" + ("%.2f" % plan.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
    #             hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
    #             payment_data["hash"] = hash
    #             response["paymentData"] = payment_data
    #             response["status"] = "ok"
    #             print(dir(company_product))
    #         except Exception as e_:
    #             print(e_)
    #             pass

    # except Exception as e:
    #     # print(e)
    #     pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_key_manager_data(request):
    response = {"status": "failed"}
    user = request.user
    # print(dir(user))

    user = request.user
    customer = user.customer
    product = CompanyProduct.objects.get(id=1)
    # print(product.name)
    plan_info = {}
    # if customer is not None:
    #     customer_has_plans = customer.customershaveplans_set.get(product=product)
    #     if customer_has_plans is not None:
    # print(dir(customer))
    if customer is not None:
        plans = customer.customershaveplans_set.filter(product=product) # 1 is the id of the KeyManager product
        # print(dir(plans))
        # print(plans)
        if len(plans) == 1:
            plan = plans[0].plan
            if plan is not None:
                planName = plan.name
                maxKeysAllowed = 10
                if planName == "Starter Tier":
                    maxKeysAllowed = 100
                elif planName == "Pro Tier":
                    maxKeysAllowed = 500
                elif planName == "Scale Tier":
                    maxKeysAllowed = 2000
                elif planName == "Enterprise Tier":
                    maxKeysAllowed = 0

                plan_info["planName"] = plan.name
                plan_info["maxKeysAllowed"] = maxKeysAllowed
            response["planActivated"] = True
            response["planInfo"] = plan_info
            # print(plan_info)
            response["status"] = "ok"
    return Response(response)



@csrf_exempt
@key_manager_api_authentication
def get_key_manager_key_information(request):
    response = {"status": "failed", "message": ""}

    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
    # print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        response["keyInformation"] = {
            "id": digital_key.id,
            "maxActivations": digital_key.max_activations,
            "currentActivations": digital_key.current_activations,
            "isActive": digital_key.is_active,
        }
        response["status"] = "ok"
    except Exception as e:
        print(e)
        response["message"] = "Invalid key provided"
    # print("Called get key state function")
    return JsonResponse(response)


"""
Update the number of activations and activations left
"""
@csrf_exempt
@key_manager_api_authentication
def activate_key(request):
    response = {"status": "failed", "message": ""}
    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
    # print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        if digital_key.is_active:
            if digital_key.current_activations < digital_key.max_activations:
                digital_key.current_activations = digital_key.current_activations + 1
                digital_key.save()
                response["status"] = "ok"
            else:
                response["message"] = "Maximum activation count reached. cannot use this key for activating. deactivate one usage of the key or increase the number of activations for the key"
        else:
            response["message"] = "Key is inactive. activation cannot be done. enable this key before activation or deactivation"
    except Exception as e:
        print(e)
        response["message"] = "Invalid key provided"
    # print("Called get key state function")
    return JsonResponse(response)

"""
Update the number of activations and activations left
"""
@csrf_exempt
@key_manager_api_authentication
def deactivate_key(request):
    response = {"status": "failed", "message": ""}
    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
    # print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        if digital_key.is_active:
            if digital_key.current_activations > 0:
                digital_key.current_activations = digital_key.current_activations - 1
                digital_key.save()
                response["status"] = "ok"
            else:
                response["message"] = "Maximum deactivation limit reached."
        else:
            response["message"] = "Key is inactive. deactivation cannot be done. enable this key before deactivation or activation"
    except Exception as e:
        print(e)
        response["message"] = "Invalid key provided"
    # print("Called get key state function")
    return JsonResponse(response)


"""
Mark the key as active. This function makes 
the provided key able to use
"""
@csrf_exempt
@key_manager_api_authentication
def mark_key_as_active(request):
    response = {"status": "failed", "message": ""}

    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
    # print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        digital_key.is_active = data["isActive"]
        digital_key.save()
        response["status"] = "ok"
    except:
        response["message"] = "Invalid key provided"
    # print("Called get key state function")
    return JsonResponse(response)



"""
Deletes the specified key
"""
@csrf_exempt
@key_manager_api_authentication
def delete_key(request):
    response = {"status": "failed", "message": ""}
    data = {}
    if request.method == "POST":
        data = json.loads(request.body)
    print(data)
    try:
        digital_key = DigitalKey.objects.get(key=data["key"])
        digital_key.delete()
        response["status"] = "ok"
    except:
        response["message"] = "Invalid key provided"
    print("Called get key state function")
    return JsonResponse(response)
