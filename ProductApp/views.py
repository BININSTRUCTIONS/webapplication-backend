from django.shortcuts import render
from django.http.response import FileResponse, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import os
from datetime import datetime
import hashlib

from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from api.models import ProductOrder, Customer, CustomersHavePlans, PaymentReceipt
from KeyManager.models import DigitalKey

from datetime import datetime

from ProductApp.models import CompanyProduct, PaymentNotificationDetail, UpgradePlanRequest, SubscriptionPlan
import json


@csrf_exempt
def handle_payment_notification(request):
    try:
        data = request.POST
        json_data = json.dumps(data)
        payment_receipt = PaymentReceipt.objects.get(order_id=data["order_id"])

        print(data)

        if payment_receipt is not None:
            hash_string = settings.PAYHERE_MERCHANT_ID + f"{payment_receipt.order_id}" + data["payhere_amount"] + "USD" + data["status_code"] + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
            hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
            print(hash)
            print(data["md5sig"])
            if hash == data["md5sig"]:
                payment_receipt.payment_id = data["payment_id"]
                payment_receipt.captured_amount = data["captured_amount"]
                payment_receipt.payhere_amount = data["payhere_amount"]
                payment_receipt.status_message = data["status_message"]
                payment_receipt.status_code = data["status_code"]
                payment_receipt.method = data["method"]
                # payment_receipt.message_type = data["message_type"]
                # payment_receipt.subscription_id = data["subscription_id"]
                payment_receipt.save()

                try:
                    print(payment_receipt.items.strip().split("-"))
                    (product, plan) = payment_receipt.items.strip().split("-")
                    company_product = CompanyProduct.objects.get(name=product)
                    subscription_plan = company_product.subscriptionplan_set.get(name=plan, price=float(payment_receipt.amount))

                    try:
                        customer_has_plan = CustomersHavePlans.objects.get(customer=payment_receipt.customer, product=company_product)
                        upgrade_plan_request = UpgradePlanRequest.objects.create(
                                                user=payment_receipt.customer.user,
                                                current_plan=customer_has_plan.plan,
                                                subscription_plan=subscription_plan,
                                                datetime=datetime.now()
                                            )
                    except Exception as ex:
                        print(ex)
                        customer_has_plan = CustomersHavePlans.objects.create(
                                    customer=payment_receipt.customer,
                                    plan=subscription_plan,
                                    date=datetime.now(),
                                    product=company_product)
                except Exception as exception:
                    print(exception)

        payment_notification_detail = PaymentNotificationDetail.objects.create(information=json_data)
        if payment_notification_detail is not None:
            return JsonResponse({'status': 'ok', 'message': 'Request processed successfully.'}, status=200)
        else:
            # Failed response
            return JsonResponse({'status': 'failed', 'message': 'Something went wrong.'}, status=400)
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'failed', 'message': 'Something went wrong.'}, status=400)

    


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_payment_notifications(request):
    payment_notifications = PaymentNotificationDetail.object.all()
    information = []
    for notification in payment_notifications:
        information.append(notification.information)
    
    return Response({"notificationInformation": information})

# Create your views here.
def download_file(request):
    # response = FileResponse(open(os.getcwd().replace("\\", '/') + "/products/RCCG/2024-08-17/y2mate.com - Adele  Set Fire To The Rain Live at The Royal Albert Hall_1080p_9TeBEjL.mp4", "rb"), as_attachment=True)
    # print(request.GET)

    order = ProductOrder.objects.filter(id=request.GET["oid"])
    product = order[0].product

    if order[0].last_download_time is None:
        product_name = product.application_name
        path_for_application = os.getcwd().replace("\\", '/') + f"/products/{product_name}"

        product_launch_date_list = os.listdir(path_for_application)
        
        latest_date = None
        for date in product_launch_date_list:
            current_date = date
            if latest_date is None:
                latest_date = current_date
            else:
                if latest_date < current_date:
                    latest_date = current_date

        path_for_application += f"/{str(latest_date)}/standalone"

        file = os.listdir(path_for_application)[0]

        path_for_application += f"/{file}"
        # print(path_for_application)
        # order.update(last_download_time=datetime.now())
        file = open(path_for_application, "rb")
        response = FileResponse(file, as_attachment=True)
        response.set_headers(file)
        # response = JsonResponse({"application_name": path_for_application, "date": str(latest_date)})
    else:
        response = HttpResponse("<h1>404 Not found.</h1>")

    return response


def activate_key_manager_plan(request):
    response = {"status": "failed"}
    data = request.data
    try:
        plan_id = data["plan"]
    except:
        pass




@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def get_saas_products(request):
    response = {"status": "failed"}
    products = []
    try:
        for product in CompanyProduct.objects.all():
            products.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "plans": []
            })

            for plan in product.subscriptionplan_set.all():
                cpm = 0
                if plan.api_information is not None:
                    cpm = plan.api_information.calls_per_minute

                products[-1]["plans"].append({
                    "plan_id": plan.id,
                    "name": plan.name,
                    "price": plan.price,
                    "term": plan.term,
                    "is_recurring": plan.is_recurring,
                    "items": [],
                    "apiInfo": {
                        "callsPerMinute": cpm
                    }
                })

                for item in plan.subscriptionplanitem_set.all():
                    products[-1]["plans"][-1]["items"].append(
                        {
                            "item_id": item.id, 
                            "item": item.item
                        }
                        )
            # print(dir(product))
        response["status"] = "ok"
    except Exception as e:
        print(e)
        pass

    response["products"] = products
    return Response(response)

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_plan_for_saas_product(request):
    response = {"status": "failed", "plans": []}
    data = request.data
    try:
        product_id = data["product_id"]
        plans = []
        # print(product_id)
        company_products = CompanyProduct.objects.get(id=product_id)
        for plan in company_products.subscriptionplan_set.all():
            response["plans"].append({
                "id": plan.id,
                "name": plan.name,
                "price": plan.price,
                "term": plan.term,
                "items": []
            })
            for item in plan.subscriptionplanitem_set.all():
                # print(item.item)
                response["plans"][-1]["items"].append(item.item)
            # print(dir(plan))
        response["status"] = "ok"
        # print(dir(company_products))
    except Exception as e:
        print(e)
        pass
    # print(response)
    return Response(response)

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def activate_plan(request):
    response = {"status": "failed"}
    data = request.data
    # print(data)
    try:
        product_id = data["productID"]
        plan_id = data["planID"]

        company_product = CompanyProduct.objects.get(id=product_id)
        if company_product is not None:
            try:
                plan = company_product.subscriptionplan_set.get(id=plan_id)
                # print(plan)
                number_of_license_keys_generated = DigitalKey.objects.filter(user=request.user)
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

                if len(number_of_license_keys_generated) > maxKeysAllowed:
                    response["status"] = "failed"
                    response["message"] = "You are trying to downgrade the subscription plan. but there are many keys generated than the limited key amount of the new plan. Delete keys generated before downgrading the plan."
                    return Response(response)
                
                payment_data = {}
                payment_data["sandbox"] = True

                recurring_period = "Month"
                if plan.term == "y":
                    recurring_period = "Year"

                try:
                    customer = Customer.objects.get(user=request.user)
                    try:
                        customer_has_plan = CustomersHavePlans.objects.get(customer=customer, product=company_product)
                        try:
                            isUpgrade = data["isUpgrade"]
                            if isUpgrade:
                                if customer_has_plan.plan != plan:
                                    
                                    now = datetime.now()
                                    order_id = f"REC-{company_product.id}{plan.id}{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}{now.microsecond}"
                                    # print(order_id)
                                    payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
                                    payment_data["return_url"] = "https://www.bininstructions.com/payment-status"
                                    payment_data["cancel_url"] = "https://www.bininstructions.com/payment-canceled"
                                    payment_data["notify_url"] = "https://api.bininstructions.com/api/v1/product/payment-status/notify"
                                    payment_data["first_name"] = request.user.first_name
                                    payment_data["last_name"] = request.user.last_name
                                    payment_data["email"] = request.user.email
                                    payment_data["phone"] = None
                                    payment_data["address"] = None
                                    payment_data["city"] = None
                                    payment_data["country"] = None
                                    payment_data["order_id"] = order_id
                                    payment_data["items"] = company_product.name + " " + plan.name
                                    payment_data["currency"] = "USD"
                                    # payment_data["recurrence"] = f"1 {recurring_period}"
                                    # payment_data["duration"] = "Forever"
                                    payment_data["amount"] = plan.price

                                    payment_receipt = PaymentReceipt.objects.create(
                                        order_id=order_id,
                                        items=company_product.name + "-" + plan.name,
                                        currency="USD",
                                        duration="Forever",
                                        amount=plan.price,
                                        date_of_payment=datetime.today(),
                                        customer=customer
                                    )

                                    if payment_receipt is not None:
                                        hash_string = settings.PAYHERE_MERCHANT_ID + f"{order_id}" + ("%.2f" % plan.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
                                        hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
                                        payment_data["hash"] = hash

                                        if plan.price >= 1:
                                            response["paymentData"] = payment_data

                                        response["launchPayment"] = plan.price >= 1

                                    customer_has_plan.plan = plan
                                    customer_has_plan.save()

                                    response["status"] = "ok"

                                    # try:
                                    #     upgrade_plan_request = UpgradePlanRequest.objects.filter(user=request.user, subscription_plan=plan)
                                    #     if len(upgrade_plan_request) > 0:
                                    #         response["message"] = "You have already a pending request for this plan"
                                    #         response["status"] = "failed"
                                    #     else:
                                    #         upgrade_plan_request = UpgradePlanRequest.objects.create(
                                    #         user=request.user,
                                    #         current_plan=customer_has_plan.plan,
                                    #         subscription_plan=plan,
                                    #         datetime=datetime.now()
                                    #         )
                                    #         if upgrade_plan_request is not None:
                                    #             response["status"] = "ok"
                                    # except:
                                    #     upgrade_plan_request = UpgradePlanRequest.objects.create(
                                    #         user=request.user,
                                    #         current_plan=customer_has_plan.plan,
                                    #         subscription_plan=plan,
                                    #         datetime=datetime.now()
                                    #     )
                                    #     if upgrade_plan_request is not None:
                                    #         response["status"] = "ok"
                                else:
                                    response["status"] = "failed"
                                    response["message"] = "Operation is not successful Because, you are trying to reactive the same package which you have already subscribed to"
                        except Exception as upgradeException:
                            print(upgradeException)
                            response["status"] = "failed"
                            response["message"] = "You already subscribed to a plan of this product. try upgrading in your profile dashboard."
                            # print(upgradeException)
                            pass
                    except Exception as error:
                        print(error)
                        
                        if plan.is_free == False:
                            now = datetime.now()
                            order_id = f"REC-{company_product.id}{plan.id}{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}{now.microsecond}"
                            # print(order_id)
                            payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
                            payment_data["return_url"] = "https://www.bininstructions.com/payment-status"
                            payment_data["cancel_url"] = "https://www.bininstructions.com/payment-canceled"
                            payment_data["notify_url"] = "https://api.bininstructions.com/api/v1/product/payment-status/notify"
                            payment_data["first_name"] = request.user.first_name
                            payment_data["last_name"] = request.user.last_name
                            payment_data["email"] = request.user.email
                            payment_data["phone"] = None
                            payment_data["address"] = None
                            payment_data["city"] = None
                            payment_data["country"] = None
                            payment_data["order_id"] = order_id
                            payment_data["items"] = company_product.name + " " + plan.name
                            payment_data["currency"] = "USD"
                            # payment_data["recurrence"] = f"1 {recurring_period}"
                            # payment_data["duration"] = "Forever"
                            payment_data["amount"] = plan.price

                            payment_receipt = PaymentReceipt.objects.create(
                                order_id=order_id,
                                items=company_product.name + "-" + plan.name,
                                currency="USD",
                                duration="Forever",
                                amount=plan.price,
                                date_of_payment=datetime.today(),
                                customer=customer
                            )

                            if payment_receipt is not None:
                                hash_string = settings.PAYHERE_MERCHANT_ID + f"{order_id}" + ("%.2f" % plan.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
                                hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
                                payment_data["hash"] = hash

                                if plan.price >= 1:
                                    response["paymentData"] = payment_data

                                response["launchPayment"] = plan.price >= 1
                            
                            response["status"] = "ok"
                except Exception as exception:
                    print(exception)
                    pass

                
                # print(dir(company_product))
            except Exception as e_:
                print(e_)
                pass

    except Exception as e:
        print(e)
        pass
    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_activated_plans(request):
    response = {"status": "failed"}
    user = request.user
    if user is not None:
        try:
            customer = Customer.objects.get(user=user)
            customers_have_products = CustomersHavePlans.objects.filter(customer=customer)
            products = []
            # print(customers_have_products)
            for item in customers_have_products:
                product = item.product
                if product is not None:
                    plan = item.plans
                    if plan is not None:
                        api_information = plan.api_information

                        products.append({
                            "id": product.id,
                            "name": product.name,
                            "description": product.description,
                            "plan": [
                                {
                                    "plan_id": plan.id,
                                    "name": plan.name,
                                    "price": plan.price,
                                    "term": plan.term,
                                    "is_recurring": plan.is_recurring
                                }
                            ],
                            "hasAPI": api_information != None
                        })
            response["products"] = products
            # print(products)
            response["status"] = "ok"
        except Exception as exception:
            # print(exception)
            pass
    return Response(response)
