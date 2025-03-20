from django.shortcuts import render
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
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

from .models import *
import datetime

from django.core.files.storage import FileSystemStorage
from django.conf import settings

# Create your views here.
@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def customer_service_chat_request(request):
    response = {"status": "failed"}
    data = request.data

    customer_email = data["email"]
    user = None
    anonymous_user = None
    customer_service_chat = None

    try:
        user = User.objects.get(email=customer_email)
    except:
        try:
            anonymous_user = AnonymousUser.objects.get(email=customer_email)
        except:
            anonymous_user = AnonymousUser.objects.create(email=customer_email)


    try:
        if user is None:
            try:
                customer_service_chat = CustomerServiceChat.objects.get(anonymous_user=anonymous_user)
            except:
                customer_service_chat = CustomerServiceChat.objects.create(anonymous_user=anonymous_user)
        else:
            try:
                customer_service_chat = CustomerServiceChat.objects.get(user=user)
            except:
                customer_service_chat = CustomerServiceChat.objects.create(user=user)

        if customer_service_chat is not None:
            response["chat_id"] = customer_service_chat.id
            response["status"] = "ok"
    except:
        pass
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def send_message_to_customer_service(request):
    response = {"status": "failed"}
    # print(files)
    # print(dir(files))
    data = request.data
    print(data)

    anonymous_user = None
    customer_service_chat = None

    if not request.user.is_superuser:
        try:
            email = data["email"]
            try:
                anonymous_user = AnonymousUser.objects.get(email=email)
                if anonymous_user is not None:
                    customer_service_chat = CustomerServiceChat.objects.get(anonymous_user=anonymous_user)
            except Exception as e:
                # print(e)
                user = User.objects.get(email=email)
                if user is not None:
                    customer_service_chat = CustomerServiceChat.objects.get(user=user)
        except Exception as e:
            print(e)
            pass
    else:
        try:
            chat_id = data["chat_id"]
            customer_service_chat = CustomerServiceChat.objects.get(id=chat_id)
        except:
            pass

    try:
        message = data["message"]
        
        # print(customer_service_chat)
        customer_service_message = None
        if not request.user.is_superuser:
            customer_service_message = CustomerServiceMessage.objects.create(
                text=message, 
                datetime=datetime.datetime.now(), 
                customer_service_chat=customer_service_chat
                )
        else:
            customer_service_message = CustomerServiceMessage.objects.create(
                text=message, 
                datetime=datetime.datetime.now(), 
                customer_service_chat=customer_service_chat,
                user=request.user
                )
        if customer_service_message is not None:
            # customer_service_chat.messages
            response["status"] = "ok"
    except Exception as exception:
        print(exception)
        try:
            files = request.FILES
            file = files["media"]
            print(file)
            # file_path = "media/customer-service-chat/"
            # storage = FileSystemStorage(location=file_path)
            # storage.save(file.name, file)
            customer_service_message = None
            if not request.user.is_superuser:
                customer_service_message = CustomerServiceMessage.objects.create(
                    text="", 
                    media=file,
                    datetime=datetime.datetime.now(), 
                    customer_service_chat=customer_service_chat)
            else:
                customer_service_message = CustomerServiceMessage.objects.create(
                    text="", 
                    media=file,
                    datetime=datetime.datetime.now(), 
                    customer_service_chat=customer_service_chat,
                    user=request.user)
                
            response["status"] = "ok"
        except Exception as media_message_exception:
            print(media_message_exception)
            pass
        pass

    # print(response)
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_customer_service_messages(request):
    response = {"status": "failed"}
    data = request.data

    user = None
    anonymous_user = None
    customer_service_chat = None

    try:
        messages = []
        email = data["email"]

        try:
            anonymous_user = AnonymousUser.objects.get(email=email)
            if anonymous_user is not None:
                customer_service_chat = CustomerServiceChat.objects.get(anonymous_user=anonymous_user)
        except Exception as e:
            # print(e)
            user = User.objects.get(email=email)
            if user is not None:
                customer_service_chat = CustomerServiceChat.objects.get(user=user)
    except Exception as e:
        try:
            chat_id = data["chat_id"]
            customer_service_chat = CustomerServiceChat.objects.get(id=chat_id)
        except Exception as e_:
            pass
        pass

    if customer_service_chat is not None:
        message_set = customer_service_chat.customerservicemessage_set.all()
        for message in message_set:
            source = ""
            if message.user == None and (anonymous_user is not None or user is not None):
                source = "Me"
            else:
                if message.user == request.user:
                    source = "Me"

            media_url = ""
            try:
                media_url = settings.DOMAIN + message.media.url
            except:
                pass

            messages.append({
                "id": message.id,
                "from": source,
                "message": message.text,
                "media": media_url,
                "datetime": str(message.datetime)
            })
            response["status"] = "ok"
        response["messages"] = messages

    print(response)
    return Response(response)


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def send_mail_to_customer_service(request):
    data = request.data
    response = {"status": "failed"}

    email = data["email"]
    message = data["message"]

    return Response({})


@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([AllowAny])
def get_customer_service_chats(request):
    response = {"status": "ok"}

    chats = []
    
    user = request.user
    if user.is_superuser:
        for chat in CustomerServiceChat.objects.all():
            client = chat.anonymous_user
            client_name = ""
            if client is None:
                client = chat.user
                client_name = client.username
                
            chats.append({
                "id": chat.id,
                "user_email": client.email,
                "username": client_name
            })
        response["chats"] = chats
        response["status"] = "ok"

    return Response(response)
