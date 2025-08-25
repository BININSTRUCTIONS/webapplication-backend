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
    IsAdminUser
)

from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.core.mail import send_mail

# from rest_framework import serializers
from django.core import serializers

from .models import *
from ProductApp.models import *

import datetime
import hashlib
import requests
import random
import string
from django.conf import settings

from requests.auth import HTTPBasicAuth

from .models import Review


# Create your views here.
@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def logIn(request):
    data = request.data
    email = data["email"]
    password = data["password"]
    remember = data["rememberMe"]

    message = ""
    status = "failed"
    access = ""
    refresh = ""
    type_ = ""
    try:
        user = User.objects.get(email=email)
        print(user)
        if user is not None:
            login(request, user)
            if check_password(password, user.password):
                print("password matches")
                try:
                    user_type = user.employee
                    type_ = "e"
                    status = "ok"
                except Exception as e:
                    try:
                        user_type = user.customer
                        type_ = "c"
                        status = "ok"
                    except Exception as _e:
                        print(_e)
                        pass
                    print("user is not an employee")
                print(type_)
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
            else:
                message = "password is incorrect!"
                print("password do not match")
    except User.DoesNotExist:
        message = "User with the provided credentials couldn't find!"

    return Response(
        {
            "status": status,
            "message": message,
            "user_type": type_,
            "access": str(access),
            "refresh": str(refresh),
        }
    )


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def register(request):
    print(request.data)

    try:
        data = request.data["data"]
        
        firstName = data["firstName"]
        lastName = data["lastName"]
        email = data["email"]
        password = data["password"]
        rememberMe = data["rememberMe"]
        agree = data["agree"]
        securityQuestion = data["securityQuestion"]
        securityQuestionAnswer = data["securityQuestionAnswer"]

        status = "failed"
        access_token = ""
        refresh_token = ""

        if agree:
            try:
                user = User.objects.create(
                    username=f"{firstName} {lastName}",
                    first_name=firstName,
                    last_name=lastName,
                    email=email,
                    password=make_password(password),
                )

                print(user == None)

                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token

                if user is not None:
                    print("User created")
                    customer = Customer.objects.create(user=user)
                    security_question = SecurityQuestion.objects.create(question=securityQuestion, answer=securityQuestionAnswer, customer=customer)
                    try:
                        newsletter_subscription = NewsletterSubscription.objects.get(email=email)
                        newsletter_subscription.delete()
                        customer.subscribed_to_newsletter = True
                        customer.save()
                    except:
                        pass

                    if security_question is not None:
                        status = "ok"
            except Exception as exception:
                print(exception)

    except Exception as e:
        print(e)
        pass

    return Response(
        {"status": status, "access": str(access_token), "refresh": str(refresh_token)}
    )


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def password_reset(request):
    response = {"status": "failed"}
    data = request.data
    print(data)
    try:
        email = data["email"]
        try:
            emailValidation = data["emailValidation"]
            if emailValidation:
                try:
                    print(email)
                    password_reset_code = 135465
                    user = User.objects.get(email=email)
                    customer = Customer.objects.get(user=user)
                    customer.password_reset_code = password_reset_code
                    customer.save()

                    response["emailValidation"] = "pass"
                    response["question"] = customer.securityquestion.question
                    response["status"] = "ok"

                    # password_reset_request_email = PasswordResetRequestEmailList.objects.create(
                    #     email=email,
                    #     code=password_reset_code
                    # )

                    # """send_mail("BININSTRUCTION Password Reset", f"Use this code to reset the password. {password_reset_code}", "bininstructions@gmail.com", [email], fail_silently=False)"""

                    # if password_reset_request_email is not None:
                    #     # print(customer.securityquestion.question)
                    #     response["question"] = customer.securityquestion.question
                    #     response["status"] = "ok"

                    print("Email sent")
                    print(response)

                    return Response(response)
                except Exception as e_:
                    print(e_)
                    response["message"] = "Invalid email. Recheck the entered email."
                    
        except Exception as e:
            print("Validating code and passwords")
            try:
                # code = data["code"]
                answer = data["answer"]
                password1 = data["password1"]
                password2 = data["password2"]
                print(data)
                if password1 == password2:
                    try:
                        user = User.objects.get(email=email)
                        customer = Customer.objects.get(user=user)
                        if customer.securityquestion.answer == answer:
                            user.password = make_password(password1)
                            customer.password_reset_code = ""
                            # try:
                                # print(email)
                                # password_reset_request = PasswordResetRequestEmailList.objects.get(email=email)
                                # password_reset_request.delete()
                            # except Exception as exception:
                                # print(exception)
                                # pass
                            user.save()
                            customer.save()
                            response["status"] = "ok"
                            print("Customer")
                            print(customer.securityquestion.answer)
                        else:
                            response["message"] == "Invalid code"
                    except Exception as e__:
                        print(e__)
                        response["message"] = "email does not exist"
                        pass
                else:
                    response["message"] = "passwords do not match"
            except Exception as e:
                print(e)
                response["message"] = "some information are missing. try again. if the issue exists, contact us"
                pass
            pass
    except Exception as e:
        pass
        # try:
        #     user = User.objects.get(email=email)
        #     if user is not None:
        #         customer = user.customer
        #         customer.password_reset_code = 1354654
        #         customer.save()

        #         send_mail("BININSTRUCTION Password Reset", f"Use this code to reset the password. {1354654}", "bininstructions@gmail.com", email, fail_silently=False)
        #         response["message"] = "We have sent a code to reset the password for the provided email. enter the code in the below textbox"
        #         response["status"] = "ok"
        #     else:
        #         response["message"] = "User with provided email does not exist. please re-check the email."
        # except:
        #     response["message"] = "User with provided email does not exist. please re-check the email."
    return Response(response)


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def validate_password_reset_code(request):
    response = {"status": "failed"}
    data = request.data

    code = data["code"]
    email = data["email"]

    try:
        user = User.objects.get(email=email)
        customer = user.customer
        if code == customer.password_reset_code:
            response["status"] = "ok"
        else:
            pass
    except:
        pass
    return Response(response)


@api_view(["POST"])
@permission_classes([])
@authentication_classes([])
def proceed_password_change(request):
    response = {"status": "failed"}
    data = request.data

    email = data["email"]

    password = data["password"]
    confirmation_password = data["confirmPassword"]
    if password == confirmation_password:
        try:
            user = User.objects.get(email=email)
            user.password = make_password(password)
            user.save()

            customer = user.customer
            customer.password_reset_code = 0
            customer.save()

            response["status"] = "ok"
        except:
            pass
    return Response(response)



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_user_information(request):
    response = {"status": "ok"}
    user = request.user
    customer = user.customer
    # print(dir(user))

    try:
        all_orders = Order.objects.filter(user=request.user)
        order_information = {
            "maxOrders": 0,
            "completedOrders": 0
        }

        project_information = {
            "maxProjects": 0,
            "completedProjects": 0,
            "finalizedProjects": 0
        }

        for order in all_orders:
            projects = order.project_set.all()
            projectsCount = len(projects)
            project_information["maxProjects"] += projectsCount
            finishedProjects = 0
            order_information["maxOrders"] += 1
            for project in projects:
                if project is not None:
                    project_information["maxProjects"] += 1
                    project_status = project.status.status
                    if project_status == "complete":
                        project_information["completedProjects"] += 1
                    elif project_status == "in progress":
                        pass
                    elif project_status == "finished":
                        project_information["finalizedProjects"] += 1
                        finishedProjects += 1
                    elif project_status == "waiting for approval":
                        pass
                    elif project_status == "approved":
                        pass
            
            if projectsCount == finishedProjects:
                order_information["completedOrders"] += 1
    except Exception as exception:
        print(exception)
        pass


    account_type = customer.account_type
    if account_type is not None:
        response["hasBusinessAccount"] = account_type.type == "business"
    else:
        response["hasBusinessAccount"] = False

    response["orderInformation"] = order_information
    response["projectInformation"] = project_information

    accountInformation = {
        "firstName": user.first_name,
        "lastName": user.last_name,
        "username": user.username,
        "email": user.email
    }

    response["accountInformation"] = accountInformation
    
    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_orders(request):
    orders = Order.objects.filter(user=request.user)
    # print(orders)

    data = {}
    for order in orders:
        order_id = order.id
        user_id = order.user.id
        username = order.user.username

        plan = order.plan

        # print(user_id, "is", username)

        data[order.id] = {
            "order": {"order_id": order_id, "user": username},
            "projects": [],
        }

        projects = Project.objects.filter(order=order)
        for project in projects:
            id = project.id
            name = project.name
            proposal_link = project.proposal_link
            design_link = project.design_link
            type = project.type.type
            status_number = project.status.id
            status = project.status.status

            start_date = project.start_date
            if start_date is not None:
                start_date = project.start_date

            end_date = project.end_date
            if end_date is not None:
                end_date = project.end_date

            project_data = {
                "id": id,
                "name": name,
                "proposal_link": proposal_link,
                "design_link": design_link,
                "type": type,
                "status_number": status_number,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "totalPayment": None,
                "recurringPayment": None,
                "term": None,
                "paymentLink": project.payment_link,
                "frontendProgress": project.frontend_progress,
                "backendProgress": project.backend_progress,
                "databaseProgress": project.database_progress,
            }

            if plan is not None:
                project_data["totalPayment"] = plan.one_time_payment
                project_data["recurringPayment"] = plan.recurring_payment
                project_data["term"] = plan.term_name

                payment_data = {}

                payment_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
                payment_data["return_url"] = None
                payment_data["cancel_url"] = None
                payment_data["notify_url"] = "http://sample.com/notify"
                payment_data["first_name"] = request.user.first_name
                payment_data["last_name"] = request.user.last_name
                payment_data["email"] = request.user.email
                payment_data["phone"] = ""
                payment_data["address"] = ""
                payment_data["city"] = ""
                payment_data["country"] = ""
                payment_data["order_id"] = project.id
                payment_data["items"] = name
                payment_data["currency"] = "USD"
                payment_data["amount"] = plan.one_time_payment

                hash_string = settings.PAYHERE_MERCHANT_ID + str(project.id) + ("%.2f" % plan.one_time_payment) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
                hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
                payment_data["hash"] = hash

                project_data["paymentInformation"] = payment_data 

            data[order.id]["projects"].append(project_data)
        # print(order.id)
        # data[order.id]["projects"] = serializers.serialize('json', projects);

    # print(projects)
    return Response({"data": data})


# class RegisterUser(APIView):
#     # queryset = User.objects.all()
#     permission_classes = [IsAuthenticatedOrReadOnly]
#     authentication_classes = [TokenAuthentication]

#     def post(self, request):
#         print(request.data)

#         data = request.data["data"]
#         firstName = data["firstName"]
#         lastName = data["lastName"]
#         email = data["email"]
#         password = data["password"]
#         rememberMe = data["rememberMe"]
#         agree = data["agree"]

#         status = "failed"
#         access_token = ""
#         refresh_token = ""

#         # user = User.objects.create(first_name=firstName, last_name=lastName, email=email, password=password)
#         # if user is not None:
#         #     access_token = AccessToken.for_user(user=user)
#         #     refresh_token = RefreshToken.for_user(user=user)
#         #     status = "ok"

#         return Response({"status": status, "access": access_token, "refresh": refresh_token})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_payment_link_to_project(request):
    response = {"status": "failed"}
    data = request.data

    project_id = data["projectID"]
    payment_link = data["paymentLink"]
    if request.user.is_superuser:
        try:
            project = Project.objects.get(id=project_id)
            project.payment_link = payment_link
            project.save()
            response["status"] = "ok"
        except Exception as e:
            pass
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_saas_product(request):
    response = {"status": "failed"}
    data = request.data
    print(data)
    try:
        date = data["date"]
        name = data["name"]
        description = data["description"]
        company_product = CompanyProduct.objects.create(
            date=date,
            name=name,
            description=description
        )
        if company_product is not None:
            response["status"] = "ok"
    except:
        pass
    return Response(response)



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_plan_for_saas_product(request):
    response = {"status": "failed"}
    data = request.data

    try:
        name = data["name"]
        price = data["price"]
        items = data["items"]
        term = data["term"]
        productID = data["productID"]
        is_recurring = data["is_recurring"]
        isFree = data["isFree"]

        print(data)

        try:
            saas_product = CompanyProduct.objects.get(id=productID)
            plan = SubscriptionPlan.objects.create(
                name=name,
                price=price,
                term=term,
                product=saas_product,
                is_recurring=is_recurring,
                is_free=isFree
            )

            if plan is not None:
                for item in items:
                    print("Item", item)
                    plan_feature = SubscriptionPlanItem.objects.create(
                        item=item['content'],
                        plan=plan
                    )

                response["status"] = "ok"
        except Exception as e_:
            print(e_)
            pass
    except Exception as e:
        print(e)
        pass

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_plan_for_saas_product(request):
    response = {"status": "failed"}
    data = request.data
    try:
        productID = data["productID"]
        planID = data["planID"]

        print(data)

        try:
            saas_product = CompanyProduct.objects.get(id=productID)
            plan = SubscriptionPlan.objects.get(id=planID)
            plan.delete()
            response["status"] = "ok"
        except Exception as e_:
            print(e_)
            pass
    except Exception as e:
        print(e)
        pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def edit_saas_plan(request):
    response = {"status": "failed"}
    data = request.data

    try:
        name = data["name"]
        price = data["price"]
        items = data["items"]
        term = data["term"]
        productID = data["productID"]
        planID = data["selectedPlanID"]
        is_recurring = data["is_recurring"]

        # print(data)

        try:
            saas_product = CompanyProduct.objects.get(id=productID)

            plan = SubscriptionPlan.objects.get(id=planID)

            plan.name=name
            plan.price=price
            plan.term=term
            plan.product=saas_product
            plan.is_recurring=is_recurring
            plan.save()

            print("Plan Saved!")
            print(plan)
            print(items)

            if plan is not None:
                for item in items:
                    print("Item", item)
                    plan_feature = SubscriptionPlanItem.objects.create(
                        item=item['content'],
                        plan=plan
                    )
                response["status"] = "ok"
        except Exception as e_:
            print(e_)
            pass
    except Exception as e:
        print(e)
        pass

    print(response)
    return Response(response)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def get_project_discussions(request):
    data = []
    employee = None
    try:
        employee = request.user.employee
    except:
        pass


    if request.user.is_superuser:
        # project_discussions = ProjectDiscussion.objects.all()
        # order_data = {}
        # for project_discussion in project_discussions:
        #     customer = project_discussion.involved_customer
        #     customer_name = customer.user.username
        #     project= project_discussion.project

        #     if order_data.keys().__contains__(customer_name):
        #         order_data[customer_name].append({
        #             "id": project_discussion.id,
        #             "project": {
        #                 "id": project.id,
        #                 "type": project.type,
        #                 "name": project.name
        #             }
        #         })
        #     else:
        #         order_data[customer_name] = [{
        #             "id": project_discussion.id,
        #             "project": {
        #                 "id": project.id,
        #                 "type": project.type,
        #                 "name": project.name
        #             }
        #         }]
        orders = Order.objects.all()
        chats = []
        for order in orders:
            projects = order.project_set.all()
            user_name = order.user.username
            order_id = order.id
            order_name = None

            project_data = []

            for project in projects:
                project_discussion = project.projectdiscussion
                if order_name is None:
                    order_name = project.name
                project_data.append({
                    "id": project.id,
                    "name": project.name,
                    "type": project.type.id
                })
                # print(dir(project_discussion))
            chats.append({
                "id": order_id,
                "name": order_name,
                "client": user_name,
                "projects": project_data
            })
        data = chats
    else:
        if employee is not None:
            # print(dir(employee))
            assigned_projects = employee.projecthasemployees_set.all()

            
            project_data = {}
            for assigned_project in assigned_projects:
                order_data = {}
                project = assigned_project.project
                order = project.order

                order_name = project.name

                if project_data.keys().__contains__(order_name):
                    project_data[order_name]["projects"].append(
                        {
                            "id": project.id,
                            "type": project.type.id,
                            "name": project.name
                        }
                    )
                else:
                    project_data[order_name] = {
                        "id": order.id,
                        "name": order_name,
                        "start_date": project.start_date,
                        "end_date": project.end_date,
                        "projects": [
                            {
                            "id": project.id,
                            "project_type": project.type.id,
                            "project_name": project.name
                            }
                        ]
                    }
                
                order_data["name"] = project.name
            # print(project_data)
            data = project_data.values()
        else:
            orders = Order.objects.filter(user=request.user)
            # print(dir(request.user))
            # print(request.user.employee)
            for order in orders:
                order_data = {}

                projects = Project.objects.filter(order=order)
                project_data = []

                for project in projects:
                    project_data.append(
                        {
                            "id": project.id,
                            "type": project.type.id,
                            "name": project.name,
                        }
                    )
                    order_data["name"] = project.name
                order_data["id"] = order.id
                order_data["start_date"] = (projects[0].start_date,)
                order_data["end_date"] = projects[0].end_date
                order_data["projects"] = project_data
                data.append(order_data)
    return Response(data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_application_types(request):
    response = {"status": "ok"}
    application_types = []
    for application_type in ApplicationType.objects.all():
        application_types.append({
            "id": application_type.id,
            "name": application_type.type
        })

    response["applicationTypes"] = application_types

    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_price_plans(request):
    response = {"status": "ok"}
    application_types = []
    for plan in PricePlan.objects.all():
        application_types.append({
            "id": plan.id,
            "name": plan.name,
            "oneTimePayment": plan.one_time_payment,
            "recurringPayment": plan.recurring_payment,
            "term": plan.term_name,
            "applicationType": {"id": plan.application_type.id, "name": plan.application_type.type}
        })

    response["plans"] = application_types

    return Response(response)



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_discussions(request):
    pass


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_project_chat(request):
    data = request.data
    user = request.user
    activeChat = data["project"]

    print("Data: ", data)

    order = None
    messages_data = []

    if request.user.is_superuser:
        print(activeChat)
        project = Project.objects.get(id=activeChat)
        project_discussion = project.projectdiscussion
        messages = project_discussion.message_set.all()
        # print(dir(project_discussion))
        for message in messages:
                isSelf = message.user == request.user
                # print(isSelf, message.text)
                media_url = None
                try:
                    media_url = settings.DOMAIN + message.media.url
                except:
                    pass

                message_info = {
                    "id": message.id,
                    "datetime": str(message.datetime),
                    "message": message.text,
                    "media": media_url,
                    "self": isSelf,
                }
                messages_data.append(message_info)
        print(messages[0].text)
    else:
        try:
            order = Order.objects.get(id=data["order_"])
        except:
            order = Order.objects.get(user=user, id=data["order_"])

        if order is not None:
            # projectType = ApplicationType.objects.get(id=activeChat)
            project = Project.objects.get(id=activeChat, order=order)
            project_discussion = ProjectDiscussion.objects.get(project=project)


            messages = project_discussion.message_set.all()


            for message in messages:
                isSelf = message.user == request.user
                # print(isSelf, message.text)
                media_url = None
                try:
                    media_url = settings.DOMAIN + message.media.url
                except:
                    pass

                message_info = {
                    "id": message.id,
                    "date_time": str(message.datetime),
                    "message": message.text,
                    "media": media_url,
                    "self": isSelf,
                }
                messages_data.append(message_info)

    return Response(messages_data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def uploadMessage(request):
    data = request.data

    user = request.user

    files = request.FILES
    print(files)

    message_content = ""
    order = None
    project = None
    status = "failed"

    try:
        message_content = data["message"]
    except:
        pass

    try:
        order = data["order"]
    except:
        pass

    try:
        project = data["project"]
    except:
        pass

    
    if project is not None:
        project = Project.objects.get(id=project)
        projectDiscussion = ProjectDiscussion.objects.get(project=project)

        message = None

        message = Message.objects.create(
                text=message_content,
                datetime=datetime.datetime.now(),
                user=user,
                project_discussion=projectDiscussion,
            )

        message.text = message_content
        # message.save()

        if len(files.keys()) != 0:
            file_path = "media/chat/" + project.name
            storage = FileSystemStorage(location=file_path)
            for key, file in files.items():
                storage.save(file.name, file)
                message.media = file
                # message.media.url = "/media/chat/" + project.name + "/" + file.name
        
        message.save()


        if message is not None:
            status = "ok"

        # print(message_content, "is received from", user.username)
    return Response({"status": status})


@api_view(["POST"])
@permission_classes([AllowAny])
@authentication_classes([])
def authenticate_admin(request):
    status = "failed"
    data = request.data
    username = data["username"]
    email = data["email"]
    password = data["password"]

    access = ""
    refresh = ""

    user = User.objects.get(username=username, email=email)
    print(user)
    if user is not None:
        if check_password(password, user.password):
            status = "ok"
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

    return Response({"status": status, "access": str(access), "refresh": str(refresh)})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def delete_plan_item(request):
    response = {"status": "failed"}
    data = request.data
    try:
        plan_id = data["planID"]
        item_id = data["itemID"]
        subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
        if subscription_plan is not None:
            # print(dir(subscription_plan))
            item = subscription_plan.subscriptionplanitem_set.get(id=item_id)
            if item is not None:
                # print(dir(item))
                item.delete()
                response["status"] = "ok"
            # items = subscription_plan.item_set
    except Exception as e:
        print(e)
        pass
    return Response(response)



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_plan_item(request):
    response = {"status": "failed"}
    data = request.data
    try:
        plan_id = data["planID"]
        item = data["item"]
        subscription_plan = SubscriptionPlan.objects.get(id=plan_id)
        if subscription_plan is not None:
            # print(dir(subscription_plan))
            item = SubscriptionPlanItem.objects.create(item=item, plan=subscription_plan)
            if item is not None:
                # print(dir(item))
                # item.delete()
                response["status"] = "ok"
            # items = subscription_plan.item_set
    except Exception as e:
        print(e)
        pass
    return Response(response)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def place_order(request):
    data = request.data
    print(data)
    # android = data["android"]
    desktop = data["desktop"]
    web = data["web"]
    combination = data["combination"]

    projectName = data["name"]
    # proposalLink = data["proposalLink"]

    projectTypes = []

    customer = Customer.objects.get(user=request.user)

    # if android:
    #     projectTypes.append(ApplicationType.objects.get(type="Android"))

    # if desktop:
    #     projectTypes.append(ApplicationType.objects.get(type="Desktop"))

    if web:
        projectTypes.append(ApplicationType.objects.get(id=2))
    elif desktop:
        projectTypes.append(ApplicationType.objects.get(id=1))
    elif combination:
        projectTypes.append(ApplicationType.objects.get(id=3))

    plan = None
    # try:
    #     plan = data["plan"]
    #     plan = PricePlan.objects.get(id=plan)
    # except:
    #     pass


    order = None
    if plan is not None:
        order = Order.objects.create(user=request.user, plan=plan)
    else:
        order = Order.objects.create(user=request.user)


    projects = []

    print(projectTypes)

    for projectType in projectTypes:
        project = Project.objects.create(
            name=projectName,
            type=projectType,
            order=order,
            status=ProjectStatus.objects.get(id=1),
        )
        projects.append(project)

        projectDiscussion = ProjectDiscussion.objects.create(
            involved_customer=customer, project=project
        )

        involvedStaff = ProjectDiscussionHasStaff.objects.create(
            project_discussion=projectDiscussion
        )

        # print(project)
    # print(projects)
    # print(order)
    status = "failed"
    if len(projects) == len(projectTypes):
        status = "ok"

    return Response({"status": status})



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_projects(request):
    user = request.user
    orders = Order.objects.all()
    order_data = []

    keyword = None

    try:
        keyword = request.GET["search"]
    except:
        pass

    status = "failed"
    try:
        for order in orders:
            data = {}
            projects = Project.objects.filter(order=order)
            if keyword is not None:
                projects = projects.filter(name__contains=keyword)
            data["name"] = projects[0].name
            data["id"] = order.id
            data["projects"] = []
            for project in projects:
                employees = []

                project_has_employees = ProjectHasEmployees.objects.filter(project=project)
                for project_has_employee in project_has_employees:
                    employee_id = project_has_employee.employee.id
                    employee_name = project_has_employee.employee.user.username
                    employee_email = project_has_employee.employee.user.email

                    employee_data = {
                        "empID": employee_id,
                        "employeeName": employee_name,
                        "email": employee_email
                    }

                    employees.append(employee_data)
                    
                project_data = {
                    "id": project.id,
                    "name": project.name,
                    "type": project.type.type,
                    "status": project.status.status,
                    "start_date": project.start_date,
                    "end_date": project.end_date,
                    "employees": employees
                }

                data["projects"].append(project_data)
            order_data.append(data)

            status = "ok"
    except Exception as e:
        print(e)
        status = "failed"

    print(status)

    return Response({"projects": order_data, "status": status})



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_project_duration(request):
    response = {"status": "failed"}
    data = request.data
    fromDate = data["from"]
    toDate = data["to"]
    id = data["id"]

    projects = Project.objects.filter(id=id)
    print(projects)

    if len(projects) == 1:
        projects.update(start_date=fromDate, end_date=toDate)
        response["status"] = "ok"

    print(data)
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def approve_project(request):
    data = request.data
    projectID = data["projectID"]

    response = {
        "status": "failed"
    }

    project_status = ProjectStatus.objects.get(id=2)

    project = Project.objects.filter(id=projectID)
    project.update(status=project_status)

    response["status"] = "ok"
    
    return Response(response)

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_project(request):
    response = {"status": "failed"}

    data = request.data

    try:
        project_id = data["projectID"]

        project = Project.objects.get(id=project_id)

        frontend = None
        backend = None
        database = None

        try:
            frontend = data["frontEnd"]
            backend = data["backEnd"]
            database = data["database"]
        except:
            pass

        if frontend is not None:
            project.frontend_progress = int(frontend)
            project.save()

        if backend is not None:
            project.backend_progress = int(backend)
            project.save()

        if database is not None:
            project.database_progress = int(database)
            project.save()

        response["status"] = "ok"
    except:
        pass

    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_employees(request):
    data = []
    status = "failed"
    employees = Employee.objects.all()
    if employees is not None:
        status = "ok"
        for employee in employees:
            emp_data = {
                "id": employee.id,
                "firstName": employee.user.first_name,
                "lastName": employee.user.last_name,
                "designation": employee.designation.name
            }

            data.append(emp_data)

    return Response({"data": data, "status": status})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_product(request):
    status = "failed"
    files = request.FILES
    print(files)
    application_name = request.data["applicationName"]
    application_price = request.data["applicationPrice"]
    application_description = request.data["applicationDescription"]
    application_executable = files["applicationExecutable"]
    application_dependencies = files["dependencies"]
    # print()
    # media_files = files["media[]"]
    # for file in media_files:
        # print(file.name)

    application_executable_path = f"{os.getcwd()}/products/{application_name}/{str(datetime.date.today())}/standalone"
    application_dependencies_path = f"{os.getcwd()}/products/{application_name}/{str(datetime.date.today())}/dependencies"

    product = Product.objects.create(
        application_name=application_name,
        price=application_price,
        description=application_description,
        standalone_application=application_executable,
        dependencies=application_dependencies,
        )
    
    product_storage = FileSystemStorage(location=application_executable_path)
    product_storage.save(application_executable.name, application_executable)

    product_storage = FileSystemStorage(location=application_dependencies_path)
    product_storage.save(application_dependencies.name, application_dependencies)

    for key in files.keys():
        if key.startswith("media-"):
            file = files[key]
            productMedia = ProductMedia.objects.create(media_file=file, product=product)
            media_storage = FileSystemStorage(location=f"{os.getcwd()}/media/{application_name}/media", base_url=None)
            media_storage.save(file.name, file)
            # print(file.name)

    if product is not None:
        status = "ok"

    # print(application_executable)
    # print(application_dependencies)
    return Response({"status": status})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def assign_employees(request):
    status = "failed"
    data = request.data
    emp_ids = data["empIds"]

    project_id = data["projectID"]

    project = Project.objects.get(id=project_id)
    print("Assigning following employees to project", project)

    for emp_id in emp_ids:
        employee = Employee.objects.get(id=emp_id)
        # project.
        project_has_employee = ProjectHasEmployees.objects.create(project=project, employee=employee)
        print(employee)

    return Response({"status": status})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_employees_for_project(request):
    data = request.data
    projectID = data["projectID"]
    employees = []

    status = "failed"

    project_has_employees = ProjectHasEmployees.objects.filter(project=Project.objects.get(id=projectID))
    for project_has_employee in project_has_employees:
        employee_id = project_has_employee.employee.id
        employee_name = project_has_employee.user.user_name

        employee_data = {
            "empID": employee_id,
            "employeeName": employee_name
        }

        employees.append(employee_data)
    status = "OK"
    return Response({"status": status, "data": employees})



@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def get_all_products(request):
    products = Product.objects.all()
    
    product_data = []
    saas_products = []
    for saas_product in CompanyProduct.objects.all():
        saas_products.append({
            "id": saas_product.id,
            "name": saas_product.name,
            "description": saas_product.description,
            "plans": []
        })

        for plan in saas_product.subscriptionplan_set.all():
                cpm = 0
                if plan.api_information is not None:
                    cpm = plan.api_information.calls_per_minute

                saas_products[-1]["plans"].append({
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
                    saas_products[-1]["plans"][-1]["items"].append(
                        {
                            "item_id": item.id, 
                            "item": item.item
                        })

    
    for product in products:
        data = {
            "id": product.id,
            "name": product.application_name,
            "price": product.price,
            "description": product.description,
        }
        media_urls = []
        for media in product.productmedia_set.all():
            media_urls.append(media.media_file.url)
        data["media"] = media_urls
        product_data.append(data)
    return Response({"data": product_data, "sassProducts": saas_products, "status": "ok"})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_plans(request):
    response = {"status": "failed"}
    data = request.data
    try:
        productID = data["productID"]
        company_product = CompanyProduct.objects.get(id=productID)
        try:
            subscription_plan_id = data["planID"]
            plan = company_product.subscriptionplan_set.get(id=subscription_plan_id)
            api_information = plan.api_information
            if api_information is not None:
                api_info = {"callsPerMinute": api_information.calls_per_minute}
            response["apiInfo"] = api_info
            response["status"] = "ok"

        except Exception as e:
            print(e)
            plans = []
            for plan in company_product.subscriptionplan_set.all():
                plans.append({
                    "id": plan.id,
                    "name": plan.name
                })
            print(plans)
            response["plans"] = plans
            response["status"] = "ok"
    except Exception as e:
        print(e)
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def set_api_info_for_plan(request):
    response = {"status": "failed"}
    data = request.data

    try:
        product_id = data["productID"]
        plan_id = data["planID"]
        calls_per_minute = data["callsPerMinute"]
        print(data)
        try:
            company_product = CompanyProduct.objects.get(id=product_id)
            try:
                print(company_product.subscriptionplan_set.all())
                plan = company_product.subscriptionplan_set.get(id=plan_id)
                api_info = plan.api_information
                if api_info is not None:
                    api_info.calls_per_minute = calls_per_minute
                    api_info.save()
                    response["status"] = "ok"
                else:
                    api_information = APIInfo.objects.create(calls_per_minute=calls_per_minute)
                    if api_information is not None:
                        plan.api_information = api_information
                        plan.save()
                        response["status"] = "ok"
            except Exception as e__:
                print(e__)
                pass
        except Exception as e_:
            print(e_)
            pass
    except Exception as e:
        print(e)

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_api_info_for_plan(request):
    response = {"status": "failed"}
    information = []

    for product in CompanyProduct.objects.all():
        information.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "date": product.date,
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "price": plan.price,
                    "term": plan.term,
                    "is_recurring": plan.is_recurring,
                    "api_information": {
                        "id": plan.api_information.id if plan.api_information != None else None,
                        "calls_per_minute": plan.api_information.calls_per_minute if plan.api_information != None else 0
                        }
                } for plan in product.subscriptionplan_set.all() if plan != None
            ]
        })

    response["status"] = "ok"
    response["information"] = information
    return Response(response)




@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def update_product_plan_information(request):
    response = {"status": "failed"}
    data = request.data

    try:
        print(data)
        productID = data["productID"]

        saas_product = CompanyProduct.objects.get(id=productID)

        try:
            name = data["name"]
            saas_product.name=name
        except:
            pass

        try:
            planID = data["selectedPlanID"]
            plan = SubscriptionPlan.objects.get(id=planID)

            plan.product=saas_product

            created_items = []

            try:
                price = data["price"]
                plan.price=price
            except:
                pass

            try:
                term = data["term"]
                plan.term=term
            except:
                pass

            try:
                is_recurring = data["is_recurring"]
                plan.is_recurring=is_recurring
            except:
                pass

            try:
                is_free = data["isFree"]
                plan.is_free=is_free
            except:
                pass

            try:
                items = data["newFeaturesToAdd"]
                print(items)
                itemsToDelete = data["featuresToDelete"]

                if len(itemsToDelete) > 0:
                    for plan_item in plan.subscriptionplanitem_set.all():
                        if itemsToDelete.__contains__(plan_item.id):
                            plan_item.delete()

                if plan is not None:
                    plan_items = plan.subscriptionplanitem_set.all()
                    for item in items:
                        if len(plan_items) > 0:
                            for plan_item in plan.subscriptionplanitem_set.all():
                                # print(dir(item))
                                if plan_item.item != item["content"]:
                                    plan_feature = SubscriptionPlanItem.objects.create(
                                        item=item['content'],
                                        plan=plan
                                    )

                                    created_items.append({
                                        "id": plan_feature.id,
                                        "item": plan_feature.item
                                    })
                        else:
                            plan_feature = SubscriptionPlanItem.objects.create(
                                item=item['content'],
                                plan=plan
                            )

                            created_items.append({
                                "id": plan_feature.id,
                                "item": plan_feature.item
                            })
                        response["items"] = created_items
                        print("plan edited successfully!")
            except Exception as e:
                print(e)
                pass
            plan.save()
        except Exception as exception:
            print(exception)
        saas_product.save()
        response["status"] = "ok"
    except Exception as e:
        print(e)
        pass

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_password_reset_email(request):
    response = {"status": "failed"}
    print(request.user.is_superuser)
    if request.user.is_superuser:
        data = []
        for email in PasswordResetRequestEmailList.objects.all():
            data.append({
                "id": email.id,
                "email": email.email,
                "code": email.code
            })
        response["status"] = "ok"
        response["data"] = data

        try:
            for email in PasswordResetRequestEmailList.objects.all():
                email.delete()
        except:
            pass

    return Response(response)



# @api_view(["GET"])
# @authentication_classes([])
# @permission_classes([])
def download_file(request):
    # user = request.user
    # order = ProductOrder.objects.filter(user=user)[-1]
    # product = order.product
    # print(product.standalone_application_path)
    print(request.GET)
    # response = FileResponse(open(os.getcwd().replace("\\", '/') + "/products/RCCG/2024-08-17/y2mate.com - Adele  Set Fire To The Rain Live at The Royal Albert Hall_1080p_9TeBEjL.mp4", "rb"), as_attachment=True)
    response = JsonResponse({})
    return response



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def add_product_update(request):
    data = request.data
    files = request.FILES

    response = {
        "status": "failed"
    }

    product_id = data["productID"]
    date = data["date"]
    file = files["file"]

    product = Product.objects.filter(id=product_id)
    path = product[0].standalone_application_path

    application_executable_path = f"{os.getcwd()}/products/{product[0].application_name}/{date}/standalone"
    application_dependencies_path = f"{os.getcwd()}/products/{product[0].application_name}/{date}/dependencies"

    application_storage_system = FileSystemStorage(location=application_executable_path)
    application_storage_system.save(file.name, file)

    product.update(standalone_application_path=application_executable_path)

    if files.keys().__contains__("dependencies"):
        dependency = files["dependencies"]
        dependency_storage_system = FileSystemStorage(location=application_dependencies_path)
        dependency_storage_system.save(dependency.name, dependency)

    response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_review(request):
    response = {"status": "failed"}
    data = request.data
    
    try:
        review = Review.objects.create(user=request.user, review=data["reviewContent"])
        if review is not None:
            response["status"] = "ok"
    except:
        pass

    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([])
def get_reviews(request):
    response = {"status": "failed"}

    reviews = []
    try:
        for review in Review.objects.all():
            reviews.append({
                "review": review.review,
                "user": review.user.first_name + " " + review.user.last_name
            })
        response["status"] = "ok"
    except:
        pass

    response["reviews"] = reviews

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def purchase_product(request):
    data = request.data
    product_id = data["product_id"]
    user = request.user

    response_data = {}

    # user = User.objects.get(email=email)
    product = Product.objects.get(id=product_id)
    response_data["status"] = "ok"

    response_data["merchant_id"] = settings.PAYHERE_MERCHANT_ID
    response_data["first_name"] = user.first_name
    response_data["last_name"] = user.last_name
    response_data["email"] = user.email
    response_data["phone"] = "0774547632"
    response_data["address"] = "Nawakkulama, Megodawewa"
    response_data["city"] = "kekirawa"
    response_data["country"] = "Sri Lanka"
    response_data["order_id"] = "1"
    response_data["items"] = product.application_name
    response_data["currency"] = "USD"
    response_data["amount"] = ("%.2f" % product.price)
    # response_data["product_name"] = product.application_name

    payment_status = PaymentStatus.objects.get(status="pending")

    productOrder = ProductOrder.objects.create(
        user=user,
        product=product,
        payment_status=payment_status,
        date=str(datetime.datetime.now())
    )

    licenseKeyString = hashlib.md5((str(product.id) + str(productOrder.id) + str(datetime.datetime.now())).encode("UTF-8")).hexdigest()
    licenseKeyString = "bininstructions-" + (product.application_name.replace(" ", "-")) + licenseKeyString

    licenseKey = LicenseKey.objects.create(license_key=licenseKeyString, order=productOrder)

    response_data["order_id"] = productOrder.id

    hash_string = settings.PAYHERE_MERCHANT_ID + str(productOrder.id) + ("%.2f" % product.price) + "USD" + hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("UTF-8")).hexdigest().upper()
    hash = hashlib.md5(hash_string.encode("UTF-8")).hexdigest().upper()
    response_data["hash"] = hash
    return Response(response_data)



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def complete_order(request):
    data = request.data
    status = "failed"

    paymentStatus = PaymentStatus.objects.get(status="complete")
    order_id = data["orderID"]

    order = ProductOrder.objects.filter(id=order_id)
    order.update(payment_status=paymentStatus)
    
    status = "ok"

    response_data = {
        "status": status,
        "OID": order_id
    }

    response = FileResponse(open(os.getcwd().replace("\\", '/') + "/products/RCCG/2024-08-17/y2mate.com - Adele  Set Fire To The Rain Live at The Royal Albert Hall_1080p_9TeBEjL.mp4", "rb"), as_attachment=True)
    return Response(response_data)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_license_keys(request):
    response_data = {}
    status = "failed"

    orders = ProductOrder.objects.filter(user=request.user)
    license_keys = []
    for order in orders:
        try:
            licenseKey = LicenseKey.objects.get(order=order)
            licenseKeyData = {
                "id": licenseKey.id,
                "appID": order.id,
                "key": licenseKey.license_key,
                "purchased_date": str(order.date),
                "product": order.product.application_name,
                "status": licenseKey.is_active
            }
            # print(licenseKey.license_key)
            license_keys.append(licenseKeyData)
        except:
            pass

    status = "ok"

    response_data["status"] = status
    response_data["data"] = license_keys

    # print(response_data)

    return Response(response_data)



@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def get_latest_product(request):
    data = request.data
    product_name = data["applicationName"]
    productID = data["productID"]
    file = open("test.txt", "rb")
    data = {}
    # fileResponse = FileResponse(file, as_attachment=True)
    return Response(data)



@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def get_product_updates(request):
    data = request.data
    product_name = data["applicationName"]
    
    return Response({})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def check_product_update(request):
    data = request.data
    licenseKey = LicenseKey.objects.get(license_key=data["licenseKey"])
    order = licenseKey.order
    product = order.product

    product_folder_path = f"{os.getcwd()}/products/{product.application_name}"
    update_date_list = os.listdir(product_folder_path)

    response = {
        "status": "ok",
        "dateList": update_date_list,
        "lastUpdate": order.last_update
        }

    # if product is not None:
        # response["product"] = "Found Product"

    return Response(response)




@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_staff_project_chat(request):
    user = request.user
    employee = Employee.objects.get(user=user)
    project_has_employee = None

    print(dir(employee))
    return Response({})



@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def validate_license(request):
    print(request.data)
    order = ProductOrder.objects.get(id=request.data["appUniqueID"])
    license_key = LicenseKey.objects.get(license_key=request.data["licenseKey"], order=order)

    # product = license_key.product

    response = {
        "validation": "",
        "message": ""
    }

    if not license_key.is_active:
        license_key.is_active = True
        license_key.save()
        response["validation"] = "success"
        response["message"] = ""
    else:
        response["validation"] = "failed"
        response["message"] = "license key is already activated"

    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_subscribed_apis(request):
    response = {"status": "failed"}
    user = request.user
    if user is not None:
        pass
    return Response(response)

@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_payment_receipts(request):
    response = {"status": "failed"}
    try:
        customer = request.user.customer

        payment_receipts = PaymentReceipt.objects.filter(customer=customer)
        
        receipts = []
        for receipt in payment_receipts:
            status = ""
            if receipt.status_code == 2:
                status = "success"
            elif receipt.status_code == 0:
                status = "pending"
            elif receipt.status_code == -1:
                status = "canceled"
            elif receipt.status_code == -2:
                status = "failed"
            elif receipt.status_code == -3:
                status = "chargedback"

            receipts.append({
                "id": receipt.id,
                "order_id": receipt.order_id,
                "captured_amount": receipt.captured_amount,
                "payhere_amount": receipt.payhere_amount,
                "status_message": receipt.status_message,
                "status": status,
                "method": receipt.method,
                "message_type": receipt.message_type,
                "first_name": receipt.customer.user.first_name,
                "last_name": receipt.customer.user.last_name,
                "email": receipt.customer.user.email,
                "phone": receipt.phone,
                "address": receipt.address,
                "city": receipt.city,
                "country": receipt.country,
                "items": receipt.items,
                "currency": receipt.currency,
                "duration": receipt.duration,
                "date": receipt.date_of_payment,
                "amount": receipt.amount
            })

        response["receipts"] = receipts
        response["status"] = "ok"
    except Exception as e:
        print(e)
        pass
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_all_users_information(request):
    response = {"status": "failed"}
    users = []
    for user in User.objects.all():
        try:
            customer = Customer.objects.get(user=user)
            print("Customer: ", user.username)
            try:
                plans = customer.customershaveplans_set.all()
                # print(plans)
                data = {"username": user.username, "plans": []}
                for plan in plans:
                    data["plans"].append({
                        "planID": plan.id
                    })
                print(data)
                users.append(data)
            except Exception as e:
                print(e)
            # print(users)
            # print(dir(customer))
        except Exception as exception:
            # print(exception)
            pass
    response["userInformation"] = users
    response["status"] = "ok"
    print(response)
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def get_payhere_subscriptions(request):
    response = {"status": "failed"}
    url = "https://sandbox.payhere.lk/merchant/v1/oauth/token"

    print(settings.PAYHERE_API_AUTHORIZATION_KEY)

    headers = {
        # "Authorization": f'Bearer {settings.PAYHERE_API_AUTHORIZATION_KEY}',
        # "Authorization": f'Bearer NEo5TUlmWWYwZkY0SkFlcWdPdHRGazNzWEVnSjVFVnlqMTZjTFFDUVplODo4TEtsa2VteUtObjRUeGtLNFRrdzVwNEtBbG82S1V2M3Q0OWN2akRYNHk1bA==',
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json={"grant_type": "client_credentials"}, auth=HTTPBasicAuth(settings.PAYHERE_API_APP_ID, settings.PAYHERE_API_APP_SECRET))
        response.raise_for_status()
        data = response.json()
        print(data)
        return Response(data, safe=False)
    except Exception as e:
        print(e)
        pass
    return Response(response)



@api_view(["POST"])
@authentication_classes([])
@permission_classes([])
def subscribe_to_newsletter(request):
    response = {"status": "failed"}
    data = request.data
    try:
        email = data["email"]
        try:
            user = User.objects.get(email=email)
            customer = Customer.objects.get(user=user)
            customer.subscribed_to_newsletter = True
            customer.save()
            response["status"] = "ok"
        except:
            newsletter_subscription = NewsletterSubscription.objects.create(email=email)
            if newsletter_subscription is not None:
                response["status"] = "ok"
    except:
        response["message"] = "email is not provided"
        pass
    return Response(response)



@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_plan_upgrade_requests(request):
    response = {"status": "failed"}
    plan_upgrade_requests = []
    for plan_upgrade_request in UpgradePlanRequest.objects.all():
        plan_upgrade_requests.append({
            "id": plan_upgrade_request.id,
            "product": plan_upgrade_request.current_plan.product.name,
            "targetProduct": plan_upgrade_request.subscription_plan.product.name,
            "currentPlan": {
                "id": plan_upgrade_request.current_plan.id,
                "name": plan_upgrade_request.current_plan.name,
                "price": plan_upgrade_request.current_plan.price
            },
            "subscriptionPlan": {
                "id": plan_upgrade_request.subscription_plan.id,
                "name": plan_upgrade_request.subscription_plan.name,
                "price": plan_upgrade_request.subscription_plan.price
            },
            "user": plan_upgrade_request.user.first_name + ' ' + plan_upgrade_request.user.last_name,
            "datetime": str(plan_upgrade_request.datetime)
        })
    response["requests"] = plan_upgrade_requests
    response["status"] = "ok"
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def approve_plan_upgrade_requests(request):
    response = {"status": "failed", "message": ""}
    data = request.data
    try:
        request_id = data["requestID"]
        upgrade_request = UpgradePlanRequest.objects.get(id=request_id)
        customer = upgrade_request.user.customer
        customer_has_plan = CustomersHavePlans.objects.get(customer=customer, plan=upgrade_request.current_plan)
        customer_has_plan.plan = upgrade_request.subscription_plan
        customer_has_plan.save()
        upgrade_request.delete()
        response["status"] = "ok"
    except Exception as e:
        print(e)
        response["message"] = "Error occurred while approving the request"
        pass
    return Response(response)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminUser])
def get_lead_information(request):
    response = {"status": "failed"}

    information = {}
    for reservedSpot in ReservedSpot.objects.all():
        if information.keys().__contains__(reservedSpot.product.name):
            information[reservedSpot.product.name].append({
                "id": reservedSpot.user.id,
                "firstName": reservedSpot.user.first_name,
                "lastName": reservedSpot.user.last_name,
                "email": reservedSpot.user.email
            })
        else:
            information[reservedSpot.product.name] = [{
                "id": reservedSpot.user.id,
                "firstName": reservedSpot.user.first_name,
                "lastName": reservedSpot.user.last_name,
                "email": reservedSpot.user.email
            }]

    response["leadInfo"] = information
    response["status"] = "ok"
    return Response(response)

