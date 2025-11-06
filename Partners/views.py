from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.http.response import JsonResponse


# Create your views here.
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

import hashlib

from .models import *
from datetime import datetime
import json


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



@csrf_exempt
def handlePartnershipProductPaymentNotification(request):
    try:
        data = request.POST
        json_data = json.dumps(data)
        payment_receipt = CollaborationProductPaymentReceipt.objects.get(
            order_id=data["order_id"])

        # print(data)

        if payment_receipt is not None:
            hash_string = settings.PAYHERE_MERCHANT_ID + f"{payment_receipt.order_id}" + data["payhere_amount"] + "USD" + data["status_code"] + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
            hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
            # print(hash)
            # print(data["md5sig"])
            if hash == data["md5sig"]:
                payment_receipt.payment_id = data["payment_id"]
                payment_receipt.captured_amount = data["captured_amount"]
                payment_receipt.payhere_amount = data["payhere_amount"]
                payment_receipt.status_message = data["status_message"]
                payment_receipt.status_code = data["status_code"]
                payment_receipt.method = data["method"]
                payment_receipt.validated = True
                # payment_receipt.message_type = data["message_type"]
                # payment_receipt.subscription_id = data["subscription_id"]
                payment_receipt.save()
                return JsonResponse({'status': 'ok', 'message': 'Request processed successfully.'}, status=200)
            return JsonResponse({'status': 'failed', 'message': 'Something went wrong.'}, status=400)
        return JsonResponse({'status': 'failed', 'message': 'Something went wrong.'}, status=400)
    except Exception as e:
        # print(e)
        return JsonResponse({'status': 'failed', 'message': 'Something went wrong.'}, status=400)



@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([JWTAuthentication])
def joinWaitingList(request, productName):
    response = {"status": "failed"}
    data = request.data

    print(data)

    try:
        name = data["name"]
        website = data["website"]
        email = data["email"]
        jobTitle = data["jobTitle"]
        agreed = data["agreed"]
        payUpfront = data["payUpfront"]

        payment_data = {}
        print(data)
        if agreed:
            product = CollaborationProduct.objects.get(
                product_name=productName)
            print(product)
            print(dir(product))

            if product is not None:
                waitingUser = None
                try:
                    waitingUser = WaitingUser.objects.get(name=name)
                except Exception as exception:
                    print(exception)
                    waitingUser = WaitingUser.objects.create(
                        name=name,
                        whatsapp=whatsapp,
                        website=website,
                        email=email,
                        brandName=brandName,
                        jobTitle=jobTitle,
                        payedUpfront=payUpfront
                    )

                if waitingUser is not None:
                    try:
                        whatsapp = data["whatsapp"]
                        waitingUser.whatsapp = whatsapp
                    except:
                        pass

                    try:
                        brandName = data["brandName"]
                        waitingUser.brandName = brandName
                    except:
                        pass

                    waitingUser.save()
                    selectedPlan = None
                    try:
                        selectedPlanID = data["selectedPlan"]
                        selectedPlan = product.productplan_set.get(id=selectedPlanID)

                        if payUpfront and selectedPlan.isExclusive:
                            now = datetime.now()
                            orderID = f"REC-{product.id}{selectedPlan.id}{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}{now.microsecond}"
                            payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
                            payment_data["return_url"] = "https://www.bininstructions.com/payment-status"
                            payment_data["cancel_url"] = "https://www.bininstructions.com/payment-canceled"
                            payment_data["notify_url"] = "https://api.bininstructions.com/api/v1/partners/products/payment-status/notify"
                            payment_data["first_name"] = name
                            payment_data["last_name"] = ""
                            payment_data["email"] = email
                            payment_data["phone"] = None
                            payment_data["address"] = None
                            payment_data["city"] = None
                            payment_data["country"] = None
                            payment_data["order_id"] = orderID
                            payment_data["items"] = productName + " " + selectedPlan.planName
                            payment_data["currency"] = "USD"
                            # payment_data["recurrence"] = f"1 {recurring_period}"
                            # payment_data["duration"] = "Forever"
                            payment_data["amount"] = selectedPlan.price
                            response["paymentData"] = payment_data

                            payment_receipt = CollaborationProductPaymentReceipt.objects.create(
                                order_id=orderID,
                                items=productName + "-" + selectedPlan.planName,
                                currency="USD",
                                duration="Forever",
                                amount=selectedPlan.price,
                                date_of_payment=datetime.today(),
                                customer=waitingUser
                            )

                            if payment_receipt is not None:
                                hash_string = settings.PAYHERE_MERCHANT_ID + f"{orderID}" + ("%.2f" % selectedPlan.price) + "USD" + hashlib.md5(
                                    settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
                                hash = hashlib.md5(hash_string.encode(
                                    "UTF-8")).hexdigest().upper()
                                payment_data["hash"] = hash

                                if selectedPlan.price >= 1:
                                    response["paymentData"] = payment_data

                                response["launchPayment"] = selectedPlan.price >= 1
                    except:
                        pass

                    print("adding products")
                    waitingUserHasProduct = None

                    if selectedPlan is not None:
                        waitingUserHasProduct = WaitingUserHasProduct.objects.create(product=product, waiting_user=waitingUser, plan=selectedPlan)
                    else:
                        waitingUserHasProduct = WaitingUserHasProduct.objects.create(product=product, waiting_user=waitingUser)
                    if waitingUserHasProduct is not None:
                        #if waitingUserHasProduct is not None:
                        # waitingUser.product.add(product)
                        response["status"] = "ok"
    except Exception as e:
        print(e)
        pass

    print(response)
    return Response(response)


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([JWTAuthentication])
def sendMessage(request, productName):
    response = {"status": "failed"}
    data = request.data

    try:
        fullName = data["fullName"]
        email = data["email"]
        companyBrand = data["company"]
        useCase = data["useCase"]
        message = data["message"]

        product = CollaborationProduct.objects.get(product_name=productName)

        if product is not None:
            message = CollaborationProductMessage.objects.create(
                fullName=fullName,
                email=email,
                companyBrand=companyBrand,
                useCase=useCase,
                message=message,
                product=product
            )
            if message is not None:
                async_to_sync(get_channel_layer().group_send)(
                    "adminNotificationUpdate",
                    {
                        "type": "notify",
                        "message": "You got a message regarding Product Amplora"
                    }
                )
                response["status"] = "ok"
    except Exception as e:
        print(e)
        pass

    return Response(response)


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([JWTAuthentication])
def getPlans(request, productName):
    response = {"status": "failed"}
    plans = []
    try:
        product = CollaborationProduct.objects.get(product_name=productName)
        if product is not None:
            for plan in product.productplan_set.all():
                if plan.available:
                    plans.append({
                        "id": plan.id,
                        "planName": plan.planName,
                        "price": plan.price,
                        "available": plan.available
                    })
            response["plans"] = plans
            response["status"] = "ok"
    except Exception as e:
        print(e)
        pass
    print()
    return Response(response)
