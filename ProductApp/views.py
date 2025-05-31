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

from api.models import ProductOrder, Customer, CustomersHavePlans

from ProductApp.models import CompanyProduct, PaymentNotificationDetail
import json


@csrf_excempt
def handle_payment_notification(request):
    data = request.POST
    json_data = json.dumps(data)
    print(dir(request))
    print(json_data)
    payment_notification_detail = PaymentNotificationDetail.objects.create(information=json_data)
    if payment_notification_detail is not None:
        return JsonResponse({'status': 'ok', 'message': 'Request processed successfully.'}, status=200)
    else:
        # Failed response
        return JsonResponse({'status': 'fail', 'message': 'Something went wrong.'}, status=400)
    


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
        print(path_for_application)
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
        print(product_id)
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
    print(data)
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
                    try:
                        customer_has_plan = CustomersHavePlans.objects.get(customer=customer, product=company_product)
                        response["status"] = "failed"
                        response["message"] = "You already subscribed to a plan of this product. try upgrading in your profile dashboard."
                    except:
                        customer_has_plan = CustomersHavePlans.objects.create(
                            customer=customer,
                            plan=plan,
                            date=datetime.now())
                        
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
                        payment_data["order_id"] = f"{company_product.id}-{plan.id}-{request.user.email}"
                        payment_data["items"] = company_product.name + " " + plan.name
                        payment_data["currency"] = "USD"
                        payment_data["recurrence"] = f"1 {recurring_period}"
                        payment_data["duration"] = "Forever"
                        payment_data["amount"] = plan.price

                        hash_string = settings.PAYHERE_MERCHANT_ID + f"{company_product.id}-{plan.id}-{request.user.email}" + ("%.2f" % plan.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
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
            print(exception)
            pass
    return Response(response)
